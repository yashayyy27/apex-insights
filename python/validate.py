"""Executable data contract checks; failures stop publication of insights."""
import json
import sqlite3
import pandas as pd
import numpy as np
from common import ROOT, CONFIG, read_tables, write_json, sha256
from contracts import CONTRACTS, relationships

def inspect_frame(domain, name, frame):
    findings = []
    contract = CONTRACTS[(domain, name)]
    def check(label, condition, detail=''):
        findings.append(dict(check=f'{domain}.{name}.{label}', passed=bool(condition), detail=str(detail)))
    check('nonempty', len(frame)>0, len(frame))
    check('primary_key', not frame.duplicated(contract['key']).any(), ','.join(contract['key']))
    required = [c for c in frame if c not in contract['nullable']]
    check('required_not_null', not frame[required].isna().any().any())
    valid_classes = ['SYNTHETIC'] if domain=='fmcg' else ['PUBLIC', 'PUBLIC_DERIVED']
    check('provenance', frame.DataClass.isin(valid_classes).all())
    for col in ['Units','Revenue','COGS','VolumeLitres','TargetUnits','TargetRevenue','MarketRevenue','Points','Trials','RepeatWithin28d','DurationSeconds','LapSeconds']:
        if col in frame:
            check(col+'_nonnegative', frame[col].dropna().ge(0).all())
    if 'Date' in frame:
        dates = pd.to_datetime(frame.Date,errors='coerce')
        check('valid_dates', dates.notna().all())
        check('date_scope', dates.between(CONFIG['commercial_start'],CONFIG['commercial_end']).all())
    if name=='FactSales':
        check('revenue_identity', np.allclose(frame.Revenue,frame.Units*frame.NetPrice,rtol=0,atol=.011))
        check('cogs_identity', np.allclose(frame.COGS,frame.Units*frame.UnitCost,rtol=0,atol=.011))
        check('gross_profit_identity', np.allclose(frame.GrossProfit,frame.Revenue-frame.COGS,rtol=0,atol=.011))
        check('margin_possible', (frame.GrossProfit<=frame.Revenue).all())
        check('discount_bounds', frame.DiscountDepth.between(0,1,inclusive='left').all())
    if name=='FactDistribution':
        check('distribution_bounds', (frame.ActiveStoreDays<=frame.EligibleStoreDays).all() and frame.ActiveStoreDays.ge(0).all())
    if name=='FactInnovationPanel':
        check('repeat_bounds', (frame.RepeatWithin28d<=frame.Trials).all())
        check('cohort_complete', (pd.to_datetime(frame.Date)+pd.Timedelta(days=34)<=pd.Timestamp(CONFIG['commercial_end'])).all())
    if name in ['FactRaceResults','FactSprintResults']:
        check('unique_finishes', not frame.duplicated(['RaceKey','FinishPosition']).any())
        check('finish_bounds', frame.FinishPosition.between(1,30).all())
        check('grid_bounds', frame.Grid.between(0,30).all())
        check('points_bound', frame.Points.between(0,26 if name=='FactRaceResults' else 8).all())
        expected_completion=frame.Status.isin(['Finished','Lapped'])|frame.Status.str.fullmatch(r'\+\d+ Laps?',na=False)
        check('completion_status_mapping',frame.ClassifiedFinish.eq(expected_completion.astype(int)).all(),'Finished/Lapped and legacy +N Lap(s) are completed; retirement/DNS/DSQ are not')
        eligible = frame.ClassifiedFinish.eq(1)&frame.Grid.gt(0)
        check('movement_population', frame.PositionGain.notna().equals(eligible))
        check('movement_identity', np.allclose(frame.loc[eligible,'PositionGain'],frame.loc[eligible,'Grid']-frame.loc[eligible,'FinishPosition']))
    return findings

def validate_all():
    findings=[]
    tables={domain:read_tables(domain) for domain in ['fmcg','f1','public']}
    for domain,frames in tables.items():
        expected={name for dom,name in CONTRACTS if dom==domain}
        findings.append(dict(check=domain+'.table_coverage',passed=expected.issubset(frames),detail=str(sorted(expected-set(frames)))))
        for name,frame in frames.items():
            if (domain,name) in CONTRACTS:
                findings+=inspect_frame(domain,name,frame)
        for fact,fk,dim,dk in relationships(domain):
            ok=fact in frames and dim in frames and frames[fact][fk].isin(frames[dim][dk]).all()
            findings.append(dict(check=f'{domain}.{fact}.{fk}.foreign_key',passed=bool(ok),detail=dim))
    s=tables['fmcg']['FactSales']
    p=tables['fmcg']['DimProduct'].set_index('ProductKey')
    cust=tables['fmcg']['DimCustomer'].set_index('CustomerKey')
    findings.extend([
        dict(check='fmcg.category_alignment',passed=bool((s.CategoryKey==s.ProductKey.map(p.CategoryKey)).all()),detail='Fact SKU/category consistency'),
        dict(check='fmcg.channel_alignment',passed=bool((s.ChannelKey==s.CustomerKey.map(cust.ChannelKey)).all()),detail='Fact account/channel consistency'),
        dict(check='fmcg.region_alignment',passed=bool((s.RegionKey==s.CustomerKey.map(cust.RegionKey)).all()),detail='Fact account/region consistency'),
        dict(check='fmcg.volume_identity',passed=bool(np.allclose(s.VolumeLitres,s.Units*s.ProductKey.map(p.PackMl)/1000,rtol=0,atol=.00001)),detail='Litres per pack'),
        dict(check='fmcg.no_prelaunch_sales',passed=bool((pd.to_datetime(s.Date)>=pd.to_datetime(s.ProductKey.map(p.LaunchDate))).all()),detail='Launch cutoffs'),
    ])
    for fact in ['FactDistribution','FactTargets']:
        a=s[['Date','ProductKey','CustomerKey']].sort_values(['Date','ProductKey','CustomerKey']).reset_index(drop=True)
        b=tables['fmcg'][fact][a.columns].sort_values(list(a.columns)).reset_index(drop=True)
        findings.append(dict(check='fmcg.'+fact+'.same_grain',passed=a.equals(b),detail='Sales-aligned keys'))
    market=tables['fmcg']['FactMarket']
    agg=s.groupby(['Date','CategoryKey','ChannelKey','RegionKey']).Revenue.sum()
    market=market.set_index(['Date','CategoryKey','ChannelKey','RegionKey'])
    findings.append(dict(check='fmcg.market_components',passed=bool(np.allclose(market.PortfolioRevenue.reindex(agg.index),agg,rtol=0,atol=.011) and np.allclose(market.MarketRevenue,market.PortfolioRevenue+market.CompetitorRevenue,rtol=0,atol=.011)),detail='Focal sales included once'))
    promo=tables['fmcg']['FactPromotion']
    findings.append(dict(check='fmcg.promotion_profit_identity',passed=bool(np.allclose(promo.NetIncrementalProfit,promo.ActualGP-promo.BaselineGP-promo.TradeSpend,rtol=0,atol=.011)),detail='No double-counted discount'))
    dates=tables['fmcg']['DimDate'].Date
    findings.append(dict(check='fmcg.date_contiguous',passed=dates.tolist()==pd.date_range(CONFIG['commercial_start'],CONFIG['commercial_end']).strftime('%Y-%m-%d').tolist(),detail='731 daily dates'))
    f1=tables['f1']
    race=f1['DimRace'][['RaceKey','Season']]
    for type_,identity in [('Driver','DriverKey'),('Constructor','ConstructorKey')]:
        totals=[]
        for fact in ['FactRaceResults','FactSprintResults']:
            totals.append(f1[fact].merge(race,on='RaceKey',validate='many_to_one').groupby(['Season',identity]).Points.sum())
        computed=totals[0].add(totals[1],fill_value=0)
        official=f1['Fact'+type_+'Standings'].set_index(['Season',identity]).Points
        diff=official-computed.reindex(official.index,fill_value=0)
        findings.append(dict(check='f1.'+type_.lower()+'_points_reconciliation',passed=bool(diff.abs().lt(.001).all()),detail=diff[diff.abs().ge(.001)].to_dict()))
    manifest=json.loads((ROOT/'data/raw/f1/manifest.json').read_text())
    for name,meta in manifest.items():
        findings.append(dict(check='source_hash.'+name,passed=sha256(ROOT/'data/raw/f1'/name)==meta['sha256'],detail='PUBLIC raw response'))
    connection=sqlite3.connect(ROOT/'data/processed/apex.sqlite')
    findings.append(dict(check='sql.foreign_key_check',passed=not connection.execute('PRAGMA foreign_key_check').fetchall(),detail='Constrained mart'))
    residual=connection.execute('SELECT SUM(ABS(RevenueDelta-VolumeEffect-PriceMixEffect-InteractionEffect-NewProductEffect)) FROM revenue_bridge').fetchone()[0]
    findings.append(dict(check='sql.revenue_bridge',passed=abs(residual)<.01,detail=residual))
    connection.close()
    failed=[x for x in findings if not x['passed']]
    report=dict(status='PASS' if not failed else 'FAIL',checks=len(findings),failures=failed,results=findings,
                powerbi_runtime='NOT TESTED: Power BI Desktop unavailable on macOS')
    write_json(report,ROOT/'outputs/validation_report.json')
    validation_text=('# Data validation report\n\n'+f"Status: **{report['status']}**. {len(findings)} checks, {len(failed)} failures.\n\n"+
        'Machine-readable evidence: `outputs/validation_report.json`. Power BI runtime checks are separate.\n\n'+
        '\n'.join('- '+x['check']+': '+str(x['detail']) for x in failed))
    (ROOT/'docs/validation_report.md').write_text(validation_text.rstrip()+'\n')
    if failed:
        raise AssertionError(json.dumps(failed,indent=2,default=str))
    print(report['status'],len(findings),'data checks')
    return report

if __name__=='__main__':
    validate_all()
