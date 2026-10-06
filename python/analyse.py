"""Generate auditable findings, action hypotheses and Excel input extracts."""
import sqlite3
import pandas as pd
from common import ROOT, read_tables, save_csv, write_json, update_processed_manifest

def main():
    db=sqlite3.connect(ROOT/'data/processed/apex.sqlite')
    out=ROOT/'data/processed/analytics'
    views=['category_performance','channel_performance','sku_productivity','promotion_evaluation','innovation_review','revenue_bridge','driver_intelligence','teammate_comparison','gp_points_progression','pit_consistency']
    frames={name:pd.read_sql_query('SELECT * FROM '+name,db) for name in views}
    for name,frame in frames.items():
        save_csv(frame,out/(name+'.csv'))
    monthly=pd.read_sql_query('''SELECT Year,YearMonth,Category,Channel,Region,SUM(Revenue) Revenue,SUM(Units) Units,SUM(GrossProfit) GrossProfit
        FROM commercial_sales GROUP BY Year,YearMonth,Category,Channel,Region''',db)
    target=pd.read_sql_query('''SELECT d.Year,d.YearMonth,cat.Category,ch.Channel,r.Region,SUM(t.TargetRevenue) TargetRevenue
        FROM fmcg_FactTargets t JOIN fmcg_DimDate d USING(Date) JOIN fmcg_DimCategory cat USING(CategoryKey)
        JOIN fmcg_DimChannel ch USING(ChannelKey) JOIN fmcg_DimRegion r USING(RegionKey)
        GROUP BY d.Year,d.YearMonth,cat.Category,ch.Channel,r.Region''',db)
    monthly=monthly.merge(target,on=['Year','YearMonth','Category','Channel','Region'],validate='one_to_one')
    save_csv(monthly,out/'management_monthly.csv')
    annual=pd.read_sql_query('SELECT Year,SUM(Revenue) Revenue,SUM(Units) Units,SUM(VolumeLitres) VolumeLitres,SUM(GrossProfit) GrossProfit FROM commercial_sales GROUP BY Year',db)
    a0,a1=annual.iloc[0],annual.iloc[1]
    cat=frames['category_performance'].query('Year==2024')
    weak=cat.sort_values('RevenueYoY').iloc[0]
    strong=cat.sort_values('RevenueDelta',ascending=False).iloc[0]
    promo=frames['promotion_evaluation'].query('Year==2024')
    negative=promo[promo.NetIncrementalProfit<0]
    sku=frames['sku_productivity'].query('Year==2024')
    eligible=sku[(sku.GrossMargin>.35)&(sku.Distribution<.70)].copy()
    eligible['Opportunity']=eligible.Revenue*(.70-eligible.Distribution)/eligible.Distribution
    best=eligible.sort_values('Opportunity',ascending=False).iloc[0]
    innovation=frames['innovation_review'].sort_values('CohortRepeatRate',ascending=False)
    launch=innovation.iloc[0]
    core_coffee=pd.read_sql_query("SELECT Year,SUM(Revenue) Revenue FROM commercial_sales WHERE Category='Coffee' AND Innovation=0 GROUP BY Year ORDER BY Year",db)
    core_coffee_yoy=float(core_coffee.iloc[1].Revenue/core_coffee.iloc[0].Revenue-1)
    actions=[
        dict(ActionKey=1,CategoryKey=int(weak.CategoryKey),Scope='FY2024 portfolio simulation',Observation=f'{weak.Category}: revenue {weak.RevenueYoY:+.1%}, volume {weak.VolumeYoY:+.1%}',
             Driver=f'Existing Coffee SKU revenue {core_coffee_yoy:+.1%}; launch revenue masks core decline',Implication='Protect contribution before adding volume incentives',Action='Review account-level distribution losses and run a controlled demand test',Monitor='Existing-SKU YoY, velocity, margin, active SKU-store-days',Evidence='category_performance + commercial_sales WHERE Innovation=0',DataClass='SYNTHETIC_DERIVED'),
        dict(ActionKey=2,CategoryKey=int(strong.CategoryKey),Scope='FY2024 portfolio simulation',Observation=f'{strong.Category}: largest absolute revenue increase, AUD {strong.RevenueDelta:,.0f}',
             Driver='Category demand growth and launch mix in generator',Implication='Growth can justify selective incremental distribution',Action='Prioritise a limited distribution trial with contribution gates',Monitor='Incremental GP after costs; velocity retention',Evidence='category_performance + revenue_bridge',DataClass='SYNTHETIC_DERIVED'),
        dict(ActionKey=3,CategoryKey=0,Scope='FY2024 campaigns simulation',Observation=f'{len(negative):,} of {len(promo):,} campaigns have positive lift but negative net incremental profit',
             Driver='Discounted price and trade spend outweigh incremental GP',Implication='Volume-only reporting can misallocate promotional investment',Action='Review deepest-discount campaigns; trial reduced depth with a holdout',Monitor='Net incremental profit, ROI, revenue delta, lift',Evidence='promotion_evaluation',DataClass='SYNTHETIC_DERIVED'),
        dict(ActionKey=4,CategoryKey=int(read_tables('fmcg')['DimProduct'].set_index('ProductKey').loc[int(best.ProductKey),'CategoryKey']),
             Scope='FY2024 scenario, unchanged velocity/price',Observation=f'{best.Product}: {best.Distribution:.1%} distribution, {best.GrossMargin:.1%} GP margin',
             Driver='Eligible distribution below 70% scenario threshold',Implication=f'Indicative revenue exposure AUD {best.Opportunity:,.0f}; not a forecast',
             Action='Test additional accounts; validate incremental demand and listing costs',Monitor='Velocity retention, contribution after listing/logistics cost',Evidence='sku_productivity; revenue × distribution gap / distribution',DataClass='SYNTHETIC_DERIVED'),
        dict(ActionKey=5,CategoryKey=int(read_tables('fmcg')['DimProduct'].set_index('ProductKey').loc[int(launch.ProductKey),'CategoryKey']),Scope='2024 launch cohorts with complete follow-up',
             Observation=f'{launch.Product}: {launch.CohortRepeatRate:.1%} 28-day repeat, {launch.Trials:,.0f} trialists',
             Driver='Simulated cohort purchase probability; compare alongside launch velocity',Implication='Repeat provides a different signal from initial sell-in',Action='Stage-gate launch expansion using repeat, margin and distribution economics',Monitor='28-day repeat, launch velocity, target attainment',Evidence='innovation_review',DataClass='SYNTHETIC_DERIVED')
    ]
    save_csv(pd.DataFrame(actions),out/'ActionCentre.csv')
    drivers=frames['driver_intelligence'].query('Season==2024 and EligibleMovementStarts>=10').sort_values('AvgClassifiedPositionGain',ascending=False)
    mover=drivers.iloc[0]
    standings=read_tables('f1')['FactConstructorStandings'].query('Season==2024').sort_values('Position')
    constructor=read_tables('f1')['DimConstructor'].set_index('ConstructorKey').Constructor
    points_gap=float(standings.iloc[0].Points-standings.iloc[1].Points)
    facts=dict(revenue_2024=float(a1.Revenue),revenue_yoy=float(a1.Revenue/a0.Revenue-1),gross_margin=float(a1.GrossProfit/a1.Revenue),
               sales_rows=len(read_tables('fmcg')['FactSales']),weak_category=weak.Category,weak_category_yoy=float(weak.RevenueYoY),
               strongest_category=strong.Category,existing_coffee_yoy=core_coffee_yoy,promo_campaigns=len(promo),negative_campaigns=len(negative),
               net_promotion_profit=float(promo.NetIncrementalProfit.sum()),negative_campaign_profit=float(negative.NetIncrementalProfit.sum()),
               top_mover=mover.Driver,top_mover_gain=float(mover.AvgClassifiedPositionGain),top_mover_n=int(mover.EligibleMovementStarts),
               champion_constructor=constructor[standings.iloc[0].ConstructorKey],constructor_points_gap=points_gap,
               bridge=frames['revenue_bridge'].drop(columns=['ProductKey','CustomerKey','DataClass']).sum().to_dict())
    write_json(facts,ROOT/'outputs/insight_metrics.json')
    write_json({'monthly':monthly.to_dict('records'),'categories':cat.to_dict('records'),
                'sku':sku.to_dict('records'),'innovation':innovation.to_dict('records'),
                'actions':actions,'metrics':facts},ROOT/'excel/management_inputs.json')
    text=f'''# Findings and action hypotheses

Generated by `python/analyse.py` from validated SQL views. Commercial values
below are **SYNTHETIC**. F1 observations are **PUBLIC_DERIVED**.

## Commercial portfolio, FY2024 (AUD ex GST)

- Revenue: **AUD {a1.Revenue:,.0f}**, **{a1.Revenue/a0.Revenue-1:+.1%}** vs FY2023; GP margin **{a1.GrossProfit/a1.Revenue:.1%}**.
- {weak.Category} revenue changed **{weak.RevenueYoY:+.1%}** and volume **{weak.VolumeYoY:+.1%}**. Existing Coffee SKU revenue changed **{core_coffee_yoy:+.1%}**; a launch masks core weakness. Decompose channel/region effects before a range decision.
- {strong.Category} added **AUD {strong.RevenueDelta:,.0f}**, the largest absolute category increase. The generator embeds category demand assumptions; this is analytical practice, not market discovery.
- **{len(negative):,}/{len(promo):,}** FY2024 campaign records show positive unit lift and negative net incremental profit. Their combined net profit delta is **AUD {negative.NetIncrementalProfit.sum():,.0f}**. Baseline is a generator counterfactual.
- {best.Product} has **{best.Distribution:.1%}** simulated distribution and **{best.GrossMargin:.1%}** GP margin. At unchanged velocity/price, 70% distribution implies **AUD {best.Opportunity:,.0f}** extra revenue exposure. This excludes costs, cannibalisation and demand saturation, so use it to design a trial.
- {launch.Product} has **{launch.CohortRepeatRate:.1%}** 28-day repeat across **{launch.Trials:,.0f}** synthetic trialists. Compare cohorts with complete follow-up only.

## F1 execution, 2023–2024

- {constructor[standings.iloc[0].ConstructorKey]} leads the official 2024 constructor table by **{points_gap:,.0f} points** over {constructor[standings.iloc[1].ConstructorKey]}. Standings include sprint points; GP-only progression is named separately.
- Among drivers with at least ten eligible 2024 starts, {mover.Driver} has the highest mean classified grid-to-finish gain: **{mover.AvgClassifiedPositionGain:+.2f}** across **{int(mover.EligibleMovementStarts)}** observations. Excluding nonfinishers and pit-lane starts introduces survivorship bias; report non-finishes alongside movement.
- Pit-duration comparisons use a transparent 10–60 second screen and race-centred comparisons. The API timing is not a stationary wheel-change measure. Circuit differences and interruptions limit interpretation.
- Bahrain and Monaco 2024 lap data are deliberately sampled. Raw lap medians cannot establish tyre degradation or clean-air pace. No tyre-compound, weather or undercut-effect claims are made.

## Actions

| Observation | Driver | Commercial implication | Action hypothesis | Monitor |
|---|---|---|---|---|
'''
    for a in actions:
        text+='| '+' | '.join(a[c].replace('|','/') for c in ['Observation','Driver','Implication','Action','Monitor'])+' |\n'
    text+='\nAll actions are proposed tests. No realised business savings, team advice or deployed company outcomes are claimed.\n'
    (ROOT/'docs/insights.md').write_text(text)
    db.close()
    update_processed_manifest()
    print('Computed findings and management inputs',facts)

if __name__=='__main__':
    main()
