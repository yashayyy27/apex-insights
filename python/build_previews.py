"""Render labelled, dataset-derived reference layouts; NOT Power BI screenshots.

These images let a macOS/recruiter reader inspect the analytical design without
misrepresenting a Python render as evidence of native Power BI execution.
"""
import json
import sqlite3
import textwrap
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'outputs/matplotlib_cache'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from common import ROOT,read_tables,write_json
from build_powerbi import specs,COLORS

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titleweight':'bold','svg.fonttype':'none'})

def main():
    connection=sqlite3.connect(ROOT/'data/processed/apex.sqlite')
    query=lambda sql:pd.read_sql_query(sql,connection)
    cats=query('SELECT * FROM category_performance WHERE Year=2024').sort_values('Revenue',ascending=False)
    channel=query('SELECT * FROM channel_performance WHERE Year=2024')
    sku=query('SELECT * FROM sku_productivity WHERE Year=2024')
    promo=query('SELECT Category,SUM(ActualUnits) ActualUnits,SUM(BaselineUnits) BaselineUnits,SUM(NetIncrementalProfit) NetProfit,SUM(TradeSpend) Spend FROM promotion_evaluation WHERE Year=2024 GROUP BY Category')
    launch=query('SELECT * FROM innovation_review')
    monthly=query('SELECT YearMonth,SUM(Revenue) Revenue FROM commercial_sales WHERE Year=2024 GROUP BY YearMonth')
    plan=query('SELECT d.YearMonth,SUM(TargetRevenue) TargetRevenue FROM fmcg_FactTargets t JOIN fmcg_DimDate d USING(Date) WHERE d.Year=2024 GROUP BY d.YearMonth')
    drivers=query('SELECT * FROM driver_intelligence WHERE Season=2024')
    constructors=query('SELECT Constructor,COUNT(*) Starts,SUM(Points) GPPoints,SUM(NonFinish) NonFinishes,AVG(PositionGain) Gain,AVG(QualifyingPosition) Qualifying FROM f1_execution WHERE Season=2024 GROUP BY Constructor')
    circuits=query('SELECT Circuit,COUNT(*) Starts,AVG(PositionGain) Gain,AVG(NonFinish) NonFinishRate FROM f1_execution WHERE Season=2024 GROUP BY Circuit')
    pit=query('SELECT * FROM pit_consistency WHERE Season=2024')
    driverstand=read_tables('f1')['FactDriverStandings'].query('Season==2024').merge(read_tables('f1')['DimDriver'][['DriverKey','Driver']],on='DriverKey')
    constructorstand=read_tables('f1')['FactConstructorStandings'].query('Season==2024').merge(read_tables('f1')['DimConstructor'][['ConstructorKey','Constructor']],on='ConstructorKey')
    actions=pd.read_csv(ROOT/'data/processed/analytics/ActionCentre.csv')
    metrics=json.loads((ROOT/'outputs/insight_metrics.json').read_text())
    assets=ROOT/'assets/screenshots/reference';assets.mkdir(parents=True,exist_ok=True)
    manifest=[]

    def layout(domain,index,kpis,note):
        pal=COLORS[domain];items=specs(domain)
        fig=plt.figure(figsize=(16,10),dpi=120,facecolor=pal['bg'])
        fig.patches.append(FancyBboxPatch((0,0),.15,1,boxstyle='square,pad=0',transform=fig.transFigure,facecolor=pal['panel'],edgecolor='none',zorder=-1))
        fig.text(.021,.948,'APEX',color=pal['accent'],fontsize=23,weight='bold')
        fig.text(.021,.919,'INSIGHTS',color=pal['ink'],fontsize=14,weight='bold')
        fig.text(.021,.874,'COMMERCIAL' if domain=='fmcg' else 'PERFORMANCE',color=pal['muted'],fontsize=8)
        for i,(title,*_) in enumerate(items):
            y=.785-i*.074
            if i==index:fig.patches.append(FancyBboxPatch((.009,y-.032),.132,.064,boxstyle='round,pad=0.005,rounding_size=0.004',transform=fig.transFigure,facecolor=pal['accent'],edgecolor='none',zorder=-1))
            active_ink='#101925' if domain=='f1' else '#FFFFFF'
            fig.text(.021,y,f'{i+1:02d}  '+textwrap.fill(title,18),fontsize=10,color=active_ink if i==index else pal['muted'],va='center')
        fig.text(.177,.948,items[index][0],fontsize=25,weight='bold',color=pal['ink'])
        fig.text(.178,.908,items[index][1],fontsize=12,color=pal['muted'])
        banner='SYNTHETIC  /  FY2024  /  AUD ex GST' if domain=='fmcg' else 'SIMULATION  /  ASSUMED INPUTS  /  NO OUTCOME PREDICTION' if index==7 else 'PUBLIC-DERIVED  /  JOLPICA–ERGAST  /  2024'
        fig.text(.178,.867,banner,fontsize=9,weight='bold',color=pal['accent'])
        for j,(title,value) in enumerate(kpis):
            w=.795/len(kpis);x=.178+j*w
            fig.patches.append(FancyBboxPatch((x,.731),w-.012,.097,boxstyle='round,pad=0.005,rounding_size=0.004',transform=fig.transFigure,facecolor=pal['panel'],edgecolor='none',zorder=-1))
            fig.text(x+.012,.797,title,fontsize=9,color=pal['muted'])
            fig.text(x+.012,.756,value,fontsize=22,color=pal['ink'],weight='bold')
        axes=[]
        for j in range(4):
            x=.178+(j%2)*.409;y=.415-(j//2)*.296
            fig.patches.append(FancyBboxPatch((x,y),.393,.273,boxstyle='round,pad=0.005,rounding_size=0.004',transform=fig.transFigure,facecolor=pal['panel'],edgecolor='none',zorder=-1))
            ax=fig.add_axes([x+.083,y+.055,.284,.165],facecolor=pal['panel']);axes.append(ax)
            ax.tick_params(labelcolor=pal['muted'],colors=pal['muted'],labelsize=8,length=0)
            for spine in ax.spines.values():spine.set_visible(False)
            ax.grid(axis='x',alpha=.15,color=pal['muted']);ax.set_axisbelow(True)
        fig.text(.178,.076,textwrap.fill(note,132),fontsize=9,color=pal['muted'])
        fig.text(.178,.026,'REFERENCE PREVIEW · rendered from validated data in Python · NOT a Power BI screenshot',fontsize=9,color=pal['accent'],weight='bold')
        return fig,axes,pal

    def title(ax,text,pal):ax.set_title(text,loc='left',fontsize=11,color=pal['ink'],pad=19)
    def bar(ax,labels,values,text,pal,unit='',sort=True):
        order=np.argsort(values) if sort else np.arange(len(values))
        labels=np.asarray(labels)[order];values=np.asarray(values,dtype=float)[order]
        ax.barh(np.arange(len(values)),values,color=pal['accent'],height=.64)
        ax.set_yticks(np.arange(len(values)),[textwrap.shorten(str(x),width=23,placeholder='…') for x in labels])
        ax.set_xlabel(unit,color=pal['muted'],fontsize=8);title(ax,text,pal)
        ax.axvline(0,color=pal['muted'],lw=.5)
    def line(ax,labels,ys,text,pal,unit='',legend=None):
        for i,y in enumerate(ys):ax.plot(range(len(labels)),y,color=[pal['accent'],'#6485A0','#CBA36F'][i%3],lw=2,linestyle='-' if i==0 else '--',label=legend[i] if legend else None)
        keep=np.arange(0,len(labels),max(1,len(labels)//6));ax.set_xticks(keep,[str(labels[i])[-2:] for i in keep]);ax.set_ylabel(unit,color=pal['muted'],fontsize=8)
        if legend:ax.legend(loc='upper left',frameon=False,fontsize=8,labelcolor=pal['muted'])
        title(ax,text,pal)
    def scatter(ax,x,y,s,text,pal,xlabel,ylabel):
        ax.scatter(x,y,s=np.maximum(16,np.asarray(s)/max(s)*500),color=pal['accent'],alpha=.7,edgecolors=pal['panel'],linewidth=.7)
        ax.set_xlabel(xlabel,color=pal['muted'],fontsize=8);ax.set_ylabel(ylabel,color=pal['muted'],fontsize=8);title(ax,text,pal)
    def table(ax,headers,rows,text,pal):
        ax.set_axis_off();title(ax,text,pal)
        cells=[[textwrap.shorten(str(v),width=30 if j==0 else 19,placeholder='…') for j,v in enumerate(row)] for row in rows]
        tab=ax.table(cellText=cells,colLabels=headers,loc='center',cellLoc='left',colLoc='left',bbox=[-.12,-.1,1.2,1.1])
        tab.auto_set_font_size(False);tab.set_fontsize(8)
        for (r,c),cell in tab.get_celld().items():
            cell.set_facecolor(pal['panel']);cell.set_edgecolor(pal['panel']);cell.set_text_props(color=pal['muted'] if r==0 else pal['ink'],weight='bold' if r==0 else 'normal')
    def words(ax,text,heading,pal):
        ax.set_axis_off();title(ax,heading,pal);ax.text(-.08,.94,textwrap.fill(text,66),va='top',fontsize=9.5,color=pal['ink'],transform=ax.transAxes,linespacing=1.4)

    for domain in ['fmcg','f1']:
        for idx,(name,*_) in enumerate(specs(domain)):
            if domain=='fmcg':
                k=[('Net revenue',f'$ {metrics["revenue_2024"]/1e6:.2f}M'),('Revenue YoY',f'{metrics["revenue_yoy"]:+.1%}'),('GP margin',f'{metrics["gross_margin"]:.1%}'),('Campaigns losing value',f'{metrics["negative_campaigns"]:,}')]
                note='All beverage brands, customers, sales, costs, share and recommendations are fictional. Observed simulation results do not establish real CCEP performance.'
            else:
                note='Public F1 observations are descriptive. Non-finish selection and circuit/race timing context matter. Strategy Lab inputs are assumptions, not telemetry.'
            if domain=='f1':
                races=read_tables('f1')['DimRace'].query('Season==2024')
                k=[('Grand Prix',str(len(races))),('Driver race entries',str(len(read_tables('f1')['FactRaceResults'].query('RaceKey>=202400')))),
                   ('Constructor champion',str(constructorstand.sort_values('Position').iloc[0].Constructor)),('Title margin',f'{metrics["constructor_points_gap"]:.0f} pts')]
                if idx==7:
                    k=[('Assumed stops','2'),('Assumed pit loss','22 s'),('Assumed race length','60 laps'),('Assumed lap penalty','0.05 s/lap')]
            fig,ax,pal=layout(domain,idx,k,note)
            if domain=='fmcg':
                if idx==0:
                    line(ax[0],monthly.YearMonth,[monthly.Revenue/1e6,plan.TargetRevenue/1e6],'Revenue and plan',pal,'AUD millions',['Revenue','Plan'])
                    bar(ax[1],cats.Category,cats.Revenue/1e6,'Category contribution',pal,'AUD millions')
                    bar(ax[2],cats.Category,(cats.Revenue-cats.TargetRevenue)/1e6,'Absolute target gap',pal,'AUD millions')
                    words(ax[3],f'Coffee total sales grow {metrics["weak_category_yoy"]:.1%}, while existing Coffee SKU revenue changes {metrics["existing_coffee_yoy"]:+.1%}. Launches mask core weakness. Investigate distribution and velocity before scaling the range.','Management attention',pal)
                elif idx==1:
                    bar(ax[0],cats.Category,cats.RevenueYoY*100,'Revenue growth',pal,'% vs FY2023')
                    bar(ax[1],cats.Category,cats.GrossMargin*100,'Category gross margin',pal,'% of net revenue')
                    table(ax[2],['Category','Mix','Growth'],[[r.Category,f'{r.Contribution:.1%}',f'{r.RevenueYoY:+.1%}'] for r in cats.itertuples()],'Mix and change',pal)
                    bar(ax[3],cats.Category,cats.VolumeYoY*100,'Volume growth',pal,'% litres vs FY2023')
                elif idx==2:
                    chan=channel.groupby('Channel').agg(Revenue=('Revenue','sum'),GrossProfit=('GrossProfit','sum'),Units=('Units','sum'))
                    bar(ax[0],chan.index,chan.Revenue/1e6,'Channel revenue',pal,'AUD millions')
                    scatter(ax[1],channel.Distribution*100,channel.Velocity,channel.Revenue,'Account exposure and demand',pal,'Distribution %','Units / active SKU-store-day')
                    bar(ax[2],chan.index,chan.GrossProfit/chan.Revenue*100,'Channel margin',pal,'% gross margin')
                    bar(ax[3],channel.groupby('Region').Revenue.sum().index,channel.groupby('Region').Revenue.sum()/1e6,'Regional revenue',pal,'AUD millions')
                elif idx==3:
                    scatter(ax[0],sku.Velocity,sku.GrossMargin*100,sku.Revenue,'SKU economics',pal,'Units / active SKU-store-day','Gross margin %')
                    top=sku.nlargest(5,'Revenue');bar(ax[1],top.Product,top.Revenue/1e6,'Five highest-revenue SKUs',pal,'AUD millions')
                    seg=sku.groupby('CommercialSegment').agg(n=('ProductKey','count'),Revenue=('Revenue','sum'));bar(ax[2],seg.index,seg.n,'Within-category review segments',pal,'SKUs')
                    table(ax[3],['Segment','Revenue'],[[r[0],f'$ {r[1]/1e6:.2f}M'] for r in seg.Revenue.items()],'Commercial roles; hypotheses',pal)
                elif idx==4:
                    bar(ax[0],promo.Category,promo.ActualUnits/promo.BaselineUnits*100-100,'Promotion unit lift',pal,'% simulated counterfactual')
                    bar(ax[1],promo.Category,promo.NetProfit/1000,'Net incremental profit',pal,'AUD thousands')
                    bar(ax[2],promo.Category,promo.NetProfit/promo.Spend,'Net promotion ROI',pal,'Net profit / execution spend')
                    words(ax[3],'Discounting is already reflected in realised revenue. Actual gross profit less baseline gross profit less trade spend measures value. Positive unit lift alone is insufficient. Trial shallower discount depths with a holdout.','Decision logic',pal)
                elif idx==5:
                    bar(ax[0],launch.Product,launch.Revenue/1e6,'Launch sales',pal,'AUD millions; unequal launch windows')
                    bar(ax[1],launch.Product,launch.CohortRepeatRate*100,'28-day repeat',pal,'% complete-follow-up trialists')
                    bar(ax[2],launch.Product,launch.TargetAttainment*100,'Launch target attainment',pal,'% of independent target')
                    table(ax[3],['Launch','Velocity','Margin'],[[r.Product,f'{r.Velocity:.2f}',f'{r.GrossMargin:.1%}'] for r in launch.itertuples()],'Distribution-adjusted demand',pal)
                elif idx==6:
                    eligible=sku[(sku.GrossMargin>.35)&(sku.Distribution<.70)].copy();eligible['Exposure']=eligible.Revenue*(.70-eligible.Distribution)/eligible.Distribution;top=eligible.nlargest(5,'Exposure')
                    bar(ax[0],top.Product,top.Exposure/1e6,'70% distribution exposure',pal,'AUD millions; unchanged velocity')
                    bar(ax[1],cats.Category,(cats.Revenue-cats.TargetRevenue)/1e6,'Start with the plan gap',pal,'AUD millions')
                    b=metrics['bridge'];bar(ax[2],['Volume','Price / mix','Interaction','Launches'],[b[x]/1e6 for x in ['VolumeEffect','PriceMixEffect','InteractionEffect','NewProductEffect']],'Reconciling revenue bridge',pal,'AUD millions')
                    words(ax[3],'Investigate category → channel → region → SKU. Use the native Power BI decomposition/field-parameter source to vary the view after Windows acceptance. Indicative exposure excludes costs and cannibalisation; test velocity retention in Excel.','Investigation pathway',pal)
                else:
                    for j,a in enumerate(actions.iloc[:4].itertuples()):words(ax[j],a.Observation.rstrip('.')+'. '+a.Driver.rstrip('.')+'. '+a.Action.rstrip('.')+'. KPI: '+a.Monitor,f'Action hypothesis {j+1}',pal)
            else:
                if idx==0:
                    top=driverstand.nlargest(7,'Points');bar(ax[0],top.Driver,top.Points,'Official driver points',pal,'GP + sprint')
                    bar(ax[1],constructorstand.Constructor,constructorstand.Points,'Official constructor points',pal,'Final season standings')
                    topids=driverstand.nlargest(3,'Points').DriverKey
                    progress=query('SELECT * FROM gp_points_progression WHERE Season=2024')
                    series=[];labels=[]
                    for dk in topids:
                        g=progress[progress.DriverKey.eq(dk)].sort_values('Round');series.append(g.CumulativeGPPoints);labels.append(g.Driver.iloc[0])
                    line(ax[2],list(range(1,25)),series,'Top three: GP-only progression',pal,'Points',labels)
                    words(ax[3],'Official final standings include sprints. GP-only progression does not. Recorded GP + sprint totals reconcile for every driver and constructor in both seasons. A race/circuit slice cannot be presented as official final standings.','Scope before comparison',pal)
                elif idx==1:
                    d=drivers[drivers.EligibleMovementStarts>=10].nlargest(7,'AvgClassifiedPositionGain')
                    bar(ax[0],d.Driver,d.AvgClassifiedPositionGain,'Completed-race position gain',pal,'Mean grid minus finish; n ≥ 10')
                    scatter(ax[1],drivers.AvgQualifying,drivers.GPPoints/drivers.Starts,drivers.Starts,'Qualifying result and GP points',pal,'Mean qualifying position','GP points / entry')
                    t=query('SELECT * FROM teammate_comparison WHERE Season=2024 AND ComparableStarts>=10').nlargest(6,'AheadFinishes')
                    bar(ax[2],t.Driver,t.AheadFinishes/t.ComparableStarts*100,'Ahead of teammate',pal,'% shared completed races')
                    table(ax[3],['Driver','Gain','Eligible n'],[[r.Driver,f'{r.AvgClassifiedPositionGain:+.2f}',int(r.EligibleMovementStarts)] for r in d.head(5).itertuples()],'Sample-size context',pal)
                elif idx==2:
                    bar(ax[0],constructors.Constructor,constructors.GPPoints,'Constructor GP points',pal,'Excludes sprint')
                    bar(ax[1],constructors.Constructor,constructors.NonFinishes/constructors.Starts*100,'All-cause non-finishes',pal,'% race entries')
                    scatter(ax[2],constructors.Qualifying,constructors.GPPoints/constructors.Starts,constructors.Starts,'Qualifying conversion proxy',pal,'Mean qualifying position','GP points / entry')
                    words(ax[3],'Separate qualifying session position from penalised starting grid. Actual race constructor keys preserve driver/team changes. Non-finishes include accidents and disqualifications; this is not an engineering reliability diagnosis.','Constructor context',pal)
                elif idx==3:
                    c=circuits.nlargest(7,'Gain');bar(ax[0],c.Circuit,c.Gain,'Largest classified position movement',pal,'Mean grid minus finish')
                    c=circuits.nlargest(7,'NonFinishRate');bar(ax[1],c.Circuit,c.NonFinishRate*100,'Highest non-finish rates',pal,'% of observed 2024 entries')
                    table(ax[2],['Circuit','Entries','Non-finish'],[[r.Circuit,int(r.Starts),f'{r.NonFinishRate:.1%}'] for r in c.head(5).itertuples()],'One-season sample context',pal)
                    words(ax[3],'Grid-to-finish movement includes retirements ahead and strategy effects. It is not a count of overtakes. One season gives about 20 entries per circuit; compare the two-season model before generalising a circuit effect.','Interpretation limit',pal)
                elif idx==4:
                    windows=query('SELECT r.Race,AVG(p.LapFraction) Window FROM f1_FactPitStops p JOIN f1_DimRace r USING(RaceKey) WHERE r.Season=2024 GROUP BY r.Race ORDER BY Window LIMIT 7')
                    bar(ax[0],windows.Race,windows.Window*100,'Mean recorded pit window',pal,'% driver completed laps')
                    sample=query('SELECT RaceKey,Lap,AVG(LapSeconds) MeanLap FROM f1_FactLaps GROUP BY RaceKey,Lap ORDER BY RaceKey,Lap')
                    sample=sample[sample.RaceKey.eq(202401)];line(ax[1],sample.Lap,[sample.MeanLap],'Bahrain raw lap means',pal,'Seconds; includes pit/traffic effects')
                    words(ax[2],'Observed stops and sampled lap timing are legitimate public data. Compound, clean-air pace, safety-car context and weather are unavailable in this source. No tyre table or degradation estimate is fabricated.','Evidence boundary',pal)
                    words(ax[3],'Pit lap divided by driver completed laps is affected by retirements. Raw lap patterns do not isolate tyre condition. Use Strategy Lab only to explore explicitly assumed cost tradeoffs.','What can be concluded?',pal)
                elif idx==5:
                    bar(ax[0],pit.Constructor,pit.MedianPitDuration,'Eligible pit duration median',pal,'Seconds; API duration, not stationary service')
                    bar(ax[1],pit.Constructor,np.sqrt(pit.PopulationVariance),'Eligible duration dispersion',pal,'Population standard deviation seconds')
                    centered=query('''WITH x AS(SELECT p.ConstructorKey,p.DurationSeconds-AVG(p.DurationSeconds) OVER(PARTITION BY p.RaceKey) Delta FROM f1_FactPitStops p JOIN f1_DimRace r USING(RaceKey) WHERE r.Season=2024 AND p.TimingEligible=1) SELECT c.Constructor,AVG(Delta) Delta FROM x JOIN f1_DimConstructor c USING(ConstructorKey) GROUP BY c.Constructor''')
                    bar(ax[2],centered.Constructor,centered.Delta,'Race-centred pit duration',pal,'Seconds vs same-race mean')
                    words(ax[3],'Timing eligibility is 10–60 seconds. Excluded extremes remain in the audit. One missing Tsunoda British GP duration stays null. Circuit pit-lane length and interruptions confound raw cross-team averages.','Read before ranking',pal)
                elif idx==6:
                    scatter(ax[0],drivers.AvgQualifying,drivers.AvgFinish,drivers.Starts,'Qualifying vs classification',pal,'Mean qualifying result','Mean finishing classification')
                    d=drivers.nlargest(7,'GPPointsAboveGridBenchmark');bar(ax[1],d.Driver,d.GPPointsAboveGridBenchmark,'Points above grid benchmark',pal,'GP points delta; descriptive')
                    d=drivers.nlargest(7,'NonFinishes');bar(ax[2],d.Driver,d.NonFinishes,'All-cause non-finishes',pal,'Driver-race entries')
                    words(ax[3],'The grid benchmark awards standard top-ten points for the starting position. Delta is not causal driver value or lost championship points. Show classified movement alongside all entries and non-finishes to expose survivorship.','Execution with context',pal)
                else:
                    stops=np.arange(5);cost=[]
                    for st in stops:
                        S=st+1;q,r=divmod(60,S);cost.append(st*22+.05*((S-r)*q*(q-1)/2+r*q*(q+1)/2))
                    line(ax[0],list(map(str,stops)),[np.asarray(cost)],'SIMULATION: assumed stop tradeoff',pal,'Added seconds vs constant fresh-tyre baseline')
                    bar(ax[1],['0 stops','1 stop','2 stops','3 stops','4 stops'],cost,'SIMULATION: added-time exposure',pal,'Seconds; 60 laps, 22s pit loss, 0.05s/lap',sort=False)
                    words(ax[2],'Equal integer stints, constant pit loss, linear lap penalty reset on each stop. Inputs are assumptions, with no compounds, fuel, traffic, undercuts, safety cars or overtaking model.','SIMULATION assumptions',pal)
                    words(ax[3],'The minimum in this simplified cost model cannot predict the best real race strategy. Native Power BI What-If sources expose stop count, pit loss, degradation and race laps for sensitivity testing after runtime acceptance.','Decision boundary',pal)
            file=assets/f'{domain}_{idx+1:02d}.png';fig.savefig(file,facecolor=fig.get_facecolor());plt.close(fig)
            manifest.append(dict(domain=domain,page=name,file=str(file.relative_to(ROOT)),kind='PYTHON_REFERENCE_PREVIEW_NOT_POWER_BI_SCREENSHOT'))
    write_json(manifest,ROOT/'outputs/preview_manifest.json')
    links='\n'.join(f'<button data-file="{x["file"].replace("assets/","")}" data-title="{x["domain"].upper()} / {x["page"]}">{x["domain"].upper()} / {x["page"]}</button>' for x in manifest)
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>APEX reference preview gallery</title><style>body{margin:0;background:#101925;color:#eff5fa;font:16px system-ui}header{padding:24px 32px;border-bottom:1px solid #344457}h1{font-size:25px;margin:0 0 12px}p{color:#b0bfce;line-height:1.6;margin:4px 0}main{display:grid;grid-template-columns:280px 1fr;gap:20px;padding:24px}nav{display:grid;gap:8px;align-content:start}button{background:#192738;color:#eff5fa;border:1px solid #344457;text-align:left;border-radius:6px;padding:13px;cursor:pointer}button:hover,button.active{border-color:#51dac8;color:#51dac8}img{width:100%;height:auto;border-radius:8px}h2{font-size:18px}a{color:#51dac8}@media(max-width:900px){main{grid-template-columns:1fr}nav{grid-template-columns:repeat(2,1fr)}}</style><header><h1>APEX INSIGHTS — reference preview gallery</h1><p>Data-derived Python renders. These are <strong>not Power BI screenshots</strong> and do not demonstrate native report execution.</p><p>Power BI project sources are in <code>powerbi/</code>. Native acceptance remains pending. Commercial results are synthetic; F1 data is attributed to Jolpica–Ergast, CC BY-NC-SA 4.0.</p></header><main><nav>'''+links+'''</nav><section><h2 id="heading">Commercial / Executive Performance</h2><img id="preview" src="screenshots/reference/fmcg_01.png" alt="Labelled reference report preview"></section></main><script>const buttons=[...document.querySelectorAll('button')];buttons[0].classList.add('active');buttons.forEach(b=>b.addEventListener('click',()=>{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById('preview').src=b.dataset.file;document.getElementById('preview').alt=b.dataset.title+' reference layout, not Power BI screenshot';document.getElementById('heading').textContent=b.dataset.title;}));</script></html>'''
    (ROOT/'assets/preview.html').write_text(html)
    # A vector architecture artifact complements the editable Mermaid source.
    fig,ax=plt.subplots(figsize=(13,5),facecolor='#F3F5F7');ax.set_xlim(0,13);ax.set_ylim(0,5);ax.axis('off')
    nodes=[(.3,3.4,'Public CCEP facts\nDisconnected context'),(.3,1.8,'Jolpica API + cache\nPUBLIC / PUBLIC_DERIVED'),(.3,.2,'Seeded beverage generator\nSYNTHETIC'),(4.6,2.6,'Contracts + SQLite mart\nGrain, math, provenance'),(4.6,.6,'Analytical SQL views\nComputed actions / controls'),(9.0,3.4,'Power BI projects\nM + DAX + PBIR'),(9.0,1.8,'Excel management pack\nLive formula scenarios'),(9.0,.2,'Evidence + interview guide\nExplicit completion gates')]
    for x,y,text in nodes:
        ax.add_patch(FancyBboxPatch((x,y),3.4,1.0,boxstyle='round,pad=.06',facecolor='#FFFFFF',edgecolor='#C4CDD6'))
        ax.text(x+.18,y+.5,text,color='#172B3A',va='center',fontsize=11)
    for start,end in [((3.7,2.3),(4.6,3.1)),((3.7,.7),(4.6,3.1)),((3.7,3.9),(9,3.9)),((8,3.1),(9,3.9)),((6.3,2.6),(6.3,1.6)),((8,1.1),(9,2.3)),((8,1.1),(9,.7))]:
        ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color='#AD3045',lw=1.4))
    fig.savefig(ROOT/'assets/diagrams/architecture.svg',bbox_inches='tight');plt.close(fig)
    svg_path=ROOT/'assets/diagrams/architecture.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
    connection.close()
    print('Rendered 16 labelled reference previews and vector architecture')

if __name__=='__main__':main()
