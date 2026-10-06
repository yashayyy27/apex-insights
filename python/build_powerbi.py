"""Author native PBIP/TMSL/PBIR sources with executable DAX and M partitions.

JSON schema and field bindings can be validated here. Desktop rendering,
DAX evaluation and Power Query refresh require a Windows Power BI runtime.
"""
import json
import shutil
import uuid
import pandas as pd
from common import ROOT, CONFIG, read_tables, write_json
from contracts import CONTRACTS, relationships
from measures import FMCG, F1

BASE='https://developer.microsoft.com/json-schemas/fabric/'
DATE_COLS={'Date','WeekStart','DOB','LaunchDate','PublishedDate'}
COLORS={'fmcg':dict(bg='#F3F5F7',panel='#FFFFFF',ink='#172B3A',muted='#526777',accent='#AD3045'),
        'f1':dict(bg='#101925',panel='#192738',ink='#EFF5FA',muted='#B0BFCE',accent='#51DAC8')}

def schema(path): return BASE+path+'/schema.json'
def lit(value):
    if isinstance(value,bool): text='true' if value else 'false'
    elif isinstance(value,(int,float)): text=str(value)+'D'
    else: text="'"+str(value).replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':text}}}
def fill(color): return {'solid':{'color':lit(color)}}
def col(table,column): return {'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':column}}
def measure(name): return {'Measure':{'Expression':{'SourceRef':{'Entity':'Measures'}},'Property':name}}
def field(table,column): return col(table,column)
def qfield(spec): return measure(spec[1]) if spec[0]=='Measures' else col(*spec)
def obj(**props): return [{'properties':props}]

def type_of(frame,column):
    if column in DATE_COLS: return 'dateTime','type date'
    if pd.api.types.is_integer_dtype(frame[column]): return 'int64','Int64.Type'
    if pd.api.types.is_numeric_dtype(frame[column]): return 'double','type number'
    return 'string','type text'

LOAD_CSV='''(relativePath as text, types as list, keyColumns as list, nullableColumns as list, permittedClasses as list) as table =>
let
    Source = Csv.Document(File.Contents(DataRoot & relativePath),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Expected = List.Transform(types, each _{0}),
    SchemaChecked = if List.Sort(Table.ColumnNames(Headers)) <> List.Sort(Expected) then error "CSV schema mismatch: " & relativePath else Headers,
    Trimmed = Table.TransformColumns(SchemaChecked,List.Transform(Expected,(c)=>{c,each if _=null then null else Text.Trim(Text.From(_)),type nullable text})),
    EmptyToNull = Table.ReplaceValue(Trimmed,"",null,Replacer.ReplaceValue,Expected),
    Typed = Table.TransformColumnTypes(EmptyToNull,types,"en-AU"),
    RequiredColumns = List.Difference(Expected,nullableColumns),
    InvalidNulls = Table.SelectRows(Typed,(row)=>List.AnyTrue(List.Transform(RequiredColumns,(c)=>Record.Field(row,c)=null))),
    NullChecked = if Table.RowCount(InvalidNulls)>0 then error "Missing required value: " & relativePath else Typed,
    KeyGroups = Table.Group(NullChecked,keyColumns,{{"Rows",each Table.RowCount(_),Int64.Type}}),
    DuplicateKeys = Table.SelectRows(KeyGroups,each [Rows]>1),
    KeyChecked = if Table.RowCount(DuplicateKeys)>0 then error "Duplicate logical key: " & relativePath else NullChecked,
    InvalidClasses = Table.SelectRows(KeyChecked,each not List.Contains(permittedClasses,[DataClass])),
    Result = if Table.RowCount(InvalidClasses)>0 then error "Provenance mismatch: " & relativePath else KeyChecked
in Result'''

CALENDAR='''(startDate as date,endDate as date,dataClass as text) as table =>
let
    Dates = Table.FromList(List.Dates(startDate,Duration.Days(endDate-startDate)+1,#duration(1,0,0,0)),Splitter.SplitByNothing(),{"Date"}),
    Typed = Table.TransformColumnTypes(Dates,{{"Date",type date}}),
    Year = Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),
    MonthNumber = Table.AddColumn(Year,"MonthNumber",each Date.Month([Date]),Int64.Type),
    Month = Table.AddColumn(MonthNumber,"Month",each Date.ToText([Date],"MMM","en-AU"),type text),
    YearMonth = Table.AddColumn(Month,"YearMonth",each Date.ToText([Date],"yyyy-MM","en-AU"),type text),
    Quarter = Table.AddColumn(YearMonth,"Quarter",each "Q" & Text.From(Date.QuarterOfYear([Date])),type text),
    WeekStart = Table.AddColumn(Quarter,"WeekStart",each Date.StartOfWeek([Date],Day.Monday),type date),
    Provenance = Table.AddColumn(WeekStart,"DataClass",each dataClass,type text)
in Provenance'''

def m_list(items): return '{'+','.join('"'+str(x)+'"' for x in items)+'}'

def csv_partition(domain,name,frame):
    contract=CONTRACTS.get((domain,name),dict(key=['ActionKey'],nullable=[]))
    types='{'+','.join('{"'+c+'",'+type_of(frame,c)[1]+'}' for c in frame)+'}'
    classes=['SYNTHETIC'] if domain=='fmcg' else ['SYNTHETIC_DERIVED'] if domain=='analytics' else ['PUBLIC','PUBLIC_DERIVED']
    expression=f'fnLoadCsv("{domain}/{name}.csv",{types},{m_list(contract["key"])},{m_list(contract["nullable"])},{m_list(classes)})'
    if name=='DimDate':
        label='SYNTHETIC' if domain=='fmcg' else 'PUBLIC_DERIVED'
        return f'fnCalendar(#date(2023,1,1),#date(2024,12,31),"{label}")'
    if domain=='fmcg' and name=='DimProduct':
        # A real M mapping join, with ambiguity and orphan checks.
        expression='''let
    Base = '''+expression+''',
    Joined = Table.NestedJoin(Base,{"CategoryKey"},DimCategory,{"CategoryKey"},"CategoryMap",JoinKind.LeftOuter),
    BadMappings = Table.SelectRows(Joined,each Table.RowCount([CategoryMap])<>1),
    Checked = if Table.RowCount(BadMappings)>0 then error "Invalid category mapping" else Joined,
    NoOldCategory = Table.RemoveColumns(Checked,{"Category"}),
    Result = Table.ExpandTableColumn(NoOldCategory,"CategoryMap",{"Category"},{"Category"})
in Result'''
    return expression

def parameter_table(name,start,end,step,fmt):
    return {'name':name,'columns':[{'type':'calculatedTableColumn','name':'Value','dataType':'int64' if isinstance(step,int) else 'double','sourceColumn':'[Value]','formatString':fmt,'summarizeBy':'none','extendedProperties':[{'type':'json','name':'ParameterMetadata','value':{'version':0}}]}],
            'partitions':[{'name':name,'mode':'import','source':{'type':'calculated','expression':f'GENERATESERIES({start},{end},{step})'}}]}

def build_model(domain,label):
    tables=read_tables(domain)
    if domain=='fmcg':
        tables['ActionCentre']=pd.read_csv(ROOT/'data/processed/analytics/ActionCentre.csv')
        tables['PublicContext']=read_tables('public')['PublicContext']
    output=[]
    for name,frame in tables.items():
        columns=[]
        for c in frame:
            dtype,_=type_of(frame,c)
            column=dict(name=c,dataType=dtype,sourceColumn=c,summarizeBy='none',isHidden=c.endswith('Key') or c=='DataClass')
            if dtype=='dateTime': column['formatString']='dd MMM yyyy'
            if name=='DimDate' and c=='Date': column['isKey']=True
            if c=='Month' and 'MonthNumber' in frame: column['sortByColumn']='MonthNumber'
            columns.append(column)
        dom='analytics' if name=='ActionCentre' else 'public' if name=='PublicContext' else domain
        expr=csv_partition(dom,name,frame)
        output.append(dict(name=name,columns=columns,partitions=[dict(name=name,mode='import',source={'type':'m','expression':expr})],
                           annotations=[dict(name='DataProvenance',value='SYNTHETIC' if domain=='fmcg' and name not in ['PublicContext'] else 'PUBLIC / PUBLIC_DERIVED')],
                           **({'dataCategory':'Time'} if name=='DimDate' else {})))
    library=FMCG if domain=='fmcg' else F1
    output.append({'name':'Measures','columns':[{'name':'_Home','dataType':'int64','sourceColumn':'_Home','isHidden':True}],
                   'partitions':[{'name':'Measures','mode':'import','source':{'type':'m','expression':'#table(type table [_Home=Int64.Type],{{0}})'}}], 'measures':library})
    if domain=='fmcg':
        output.append(parameter_table('DistributionGoal',.40,.95,.05,'0%'))
        output.append({'name':'KPISelector','columns':[{'type':'calculatedTableColumn','name':'KPI','dataType':'string','sourceColumn':'[KPI]','summarizeBy':'none'}],
                       'partitions':[{'name':'KPISelector','mode':'import','source':{'type':'calculated','expression':'DATATABLE("KPI",STRING,{{"Revenue"},{"Gross margin"},{"Velocity"},{"Target attainment"}})'}}]})
        output.append({'name':'AnalysisAxis','columns':[
            {'type':'calculatedTableColumn','name':'Axis','dataType':'string','sourceColumn':'[Value1]','sortByColumn':'Order','relatedColumnDetails':{'groupByColumns':[{'groupingColumn':'Fields'}]}},
            {'type':'calculatedTableColumn','name':'Fields','dataType':'string','sourceColumn':'[Value2]','isHidden':True,'sortByColumn':'Order','extendedProperties':[{'type':'json','name':'ParameterMetadata','value':{'version':3,'kind':2}}]},
            {'type':'calculatedTableColumn','name':'Order','dataType':'int64','sourceColumn':'[Value3]','isHidden':True}],
            'partitions':[{'name':'AnalysisAxis','mode':'import','source':{'type':'calculated','expression':'{("Category",NAMEOF(DimCategory[Category]),0),("Channel",NAMEOF(DimChannel[Channel]),1),("Region",NAMEOF(DimRegion[Region]),2)}'}}]})
    else:
        output += [parameter_table('StopCount',0,4,1,'0'),parameter_table('PitLoss',15,35,1,'0 "s"'),
                   parameter_table('Degradation',0,.20,.01,'0.00 "s/lap"'),parameter_table('RaceLaps',40,80,1,'0')]
    relations=[dict(name=str(uuid.uuid5(uuid.NAMESPACE_URL,domain+'|'+ '|'.join(x))),fromTable=x[0],fromColumn=x[1],toTable=x[2],toColumn=x[3],
                    fromCardinality='many',toCardinality='one',crossFilteringBehavior='oneDirection',isActive=True) for x in relationships(domain)]
    root=ROOT/'powerbi'/f'{label}.SemanticModel'
    write_json({'$schema':schema('item/semanticModel/definitionProperties/1.0.0'),'version':'4.0','settings':{}},root/'definition.pbism')
    # DataRoot is the only machine-dependent setting; documented Windows example.
    expressions=[dict(name='DataRoot',kind='m',expression='"C:/APEX/apex-insights/data/processed/" meta [IsParameterQuery=true,Type="Text",IsParameterQueryRequired=true]'),
                 dict(name='fnLoadCsv',kind='m',expression=LOAD_CSV),dict(name='fnCalendar',kind='m',expression=CALENDAR)]
    for t in output:
        t['lineageTag']=str(uuid.uuid5(uuid.NAMESPACE_URL,label+'.'+t['name']))
        for item in t.get('columns',[])+t.get('measures',[]):
            item['lineageTag']=str(uuid.uuid5(uuid.NAMESPACE_URL,label+'.'+t['name']+'.'+item['name']))
    write_json(dict(name=label,compatibilityLevel=1601,model=dict(culture='en-AU',defaultPowerBIDataSourceVersion='powerBI_V3',
                    sourceQueryCulture='en-AU',tables=output,relationships=relations,expressions=expressions,
                    annotations=[dict(name='PBI_QueryOrder',value=json.dumps([x['name'] for x in output]))])),root/'model.bim')
    qroot=ROOT/'powerbi/power_query'/domain
    qroot.mkdir(parents=True,exist_ok=True)
    (qroot/'fnLoadCsv.m').write_text(LOAD_CSV+'\n')
    (qroot/'fnCalendar.m').write_text(CALENDAR+'\n')
    for t in output:
        partition=t['partitions'][0]['source']
        if partition['type']=='m': (qroot/(t['name']+'.m')).write_text(partition['expression']+'\n')
    dax_path=root/'DAXQueries/acceptance.dax'
    dax_path.parent.mkdir(exist_ok=True)
    dax_path.write_text('EVALUATE\n'+('SUMMARIZECOLUMNS(DimDate[Year],"Revenue",[Revenue],"GP",[Gross Profit],"Velocity",[Velocity],"MarketShare",[Simulated Market Share %])' if domain=='fmcg' else 'SUMMARIZECOLUMNS(DimSeason[Season],"Recorded",[Total Recorded Points],"OfficialDriver",[Official Driver Points],"OfficialConstructor",[Official Constructor Points])')+'\n')
    return output

def filter_config(table,column,value):
    literal={'Literal':{'Value':str(value)+'L' if isinstance(value,int) else "'"+str(value)+"'"}}
    return {'filters':[{'name':'scope_'+table+'_'+column,'type':'Categorical','field':col(table,column),
                       'filter':{'Version':2,'From':[{'Name':'d','Entity':table,'Type':0}],
                                 'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'d'}},'Property':column}}],'Values':[[literal]]}}}]}}]}

def visual(name,type_,x,y,w,h,title,roles,palette,objects=None):
    query={role:{'projections':[{'field':qfield(f),'queryRef':'.'.join(f),'nativeQueryRef':f[1],'active':True} for f in specs]} for role,specs in roles.items()}
    config=dict(visualType=type_,visualContainerObjects={
        'title':obj(show=lit(True),text=lit(title),fontColor=fill(palette['ink']),fontSize=lit(12),fontFamily=lit('Segoe UI'),titleWrap=lit(True)),
        'background':obj(show=lit(True),color=fill(palette['panel']),transparency=lit(0)),
        'border':obj(show=lit(False)),
        'visualHeader':obj(show=lit(True))})
    if roles: config['query']={'queryState':query}
    config['objects']=objects or {}
    if type_ not in ['textbox','actionButton','slicer','tableEx','decompositionTreeVisual']:
        config['objects'].update({'dataPoint':obj(defaultColor=fill(palette['accent'])),
            'categoryAxis':obj(labelColor=fill(palette['muted']),fontSize=lit(10)),
            'valueAxis':obj(labelColor=fill(palette['muted']),fontSize=lit(10)),
            'legend':obj(show=lit('Series' in roles),labelColor=fill(palette['muted']),fontSize=lit(10))})
    if type_=='card':
        config['objects'].update({'labels':obj(color=fill(palette['ink']),fontSize=lit(28)), 'categoryLabels':obj(show=lit(False))})
    if type_=='slicer':
        config['objects'].update({'items':obj(fontColor=fill(palette['ink']),background=fill(palette['panel']),textSize=lit(10)),
                                  'header':obj(fontColor=fill(palette['ink']),background=fill(palette['panel']))})
    if type_=='tableEx':
        config['objects'].update({'columnHeaders':obj(fontColor=fill(palette['muted']),backColor=fill(palette['panel']),fontSize=lit(11)),
                                  'values':obj(fontColor=fill(palette['ink']),backColor=fill(palette['panel']),fontSize=lit(10))})
    return {'$schema':schema('item/report/definition/visualContainer/2.1.0'),'name':name,
            'position':dict(x=x,y=y,width=w,height=h,z=1,tabOrder=1),'visual':config}

def textbox(name,text,x,y,w,h,palette,size=12):
    objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':text,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size)+'pt','color':palette['ink']}}]}]}}]}
    v=visual(name,'textbox',x,y,w,h,'',{},palette,objects)
    v['visual']['visualContainerObjects']['title']=obj(show=lit(False))
    v['visual']['visualContainerObjects']['background']=obj(show=lit(False))
    return v

def specs(domain):
    M=lambda *names:[('Measures',n) for n in names]
    if domain=='fmcg':
        return [
          ('Executive Performance','What happened?', ['Revenue','Volume Litres','Revenue YoY %','Gross Margin %','Simulated Market Share %','Target Attainment %'],[
           ('lineChart','Revenue and plan by month',{'Category':[('DimDate','YearMonth')],'Y':M('Revenue','Target Revenue')}),
           ('clusteredBarChart','Category contribution',{'Category':[('DimCategory','Category')],'Y':M('Revenue')}),
           ('clusteredBarChart','Plan gap by category',{'Category':[('DimCategory','Category')],'Y':M('Revenue vs Target')}),
           ('tableEx','Performance and risks',{'Values':[('DimCategory','Category')]+M('Revenue YoY %','Volume Growth %','Gross Margin %','Target Attainment %')})]),
          ('Category Performance','Where is performance changing?', ['Revenue','Revenue YoY %','Gross Margin %','Revenue Contribution %'],[
           ('clusteredBarChart','Category growth',{'Category':[('DimCategory','Category')],'Y':M('Revenue YoY %')}),
           ('lineChart','Category trajectory',{'Category':[('DimDate','YearMonth')],'Series':[('DimCategory','Category')],'Y':M('Revenue')}),
           ('tableEx','Brand and product economics',{'Values':[('DimProduct','Brand'),('DimProduct','Product'),('DimProduct','PackMl')]+M('Revenue','Gross Margin %','Selected Product Contribution %')}),
           ('clusteredBarChart','Volume growth',{'Category':[('DimCategory','Category')],'Y':M('Volume Growth %')})]),
          ('Customer and Channel','Where should commercial teams focus?', ['Revenue','Revenue YoY %','Distribution %','Velocity'],[
           ('clusteredBarChart','Channel net revenue',{'Category':[('DimChannel','Channel')],'Y':M('Revenue')}),
           ('scatterChart','Distribution and velocity',{'Category':[('DimCustomer','Customer')],'X':M('Distribution %'),'Y':M('Velocity'),'Size':M('Revenue')}),
           ('tableEx','Account performance',{'Values':[('DimCustomer','Customer')]+M('Revenue','Revenue YoY %','Gross Margin %','Distribution %','Velocity')}),
           ('clusteredBarChart','Regional plan gaps',{'Category':[('DimRegion','Region')],'Y':M('Revenue vs Target')})]),
          ('Range and SKU Productivity','Which products deserve attention?', ['Revenue','Gross Margin %','Velocity','Distribution %'],[
           ('scatterChart','SKU economics: velocity vs margin',{'Category':[('DimProduct','Product')],'X':M('Velocity'),'Y':M('Gross Margin %'),'Size':M('Revenue'),'Tooltips':M('Distribution %')}),
           ('clusteredBarChart','Product revenue',{'Category':[('DimProduct','Product')],'Y':M('Revenue')}),
           ('tableEx','Range review evidence',{'Values':[('DimProduct','Product')]+M('Revenue','SKU Revenue Rank','Gross Margin %','Velocity','Distribution %')}),
           ('clusteredBarChart','Product plan gaps',{'Category':[('DimProduct','Product')],'Y':M('Revenue vs Target')})]),
          ('Promotion and Pricing','Which promotions create profitable growth?', ['Promotion Lift %','Incremental Sales','Net Incremental Promotion Profit','Promotion ROI'],[
           ('clusteredBarChart','Net promotion profit by category',{'Category':[('DimCategory','Category')],'Y':M('Net Incremental Promotion Profit')}),
           ('scatterChart','Discount depth vs net ROI',{'Category':[('DimProduct','Product')],'X':M('Discount Depth %'),'Y':M('Promotion ROI'),'Size':M('Promoted Units')}),
           ('tableEx','Lift and value tradeoffs',{'Values':[('DimProduct','Product')]+M('Baseline Units','Incremental Units','Discount Depth %','Net Incremental Promotion Profit','Promotion ROI')}),
           ('lineChart','Promotion value through time',{'Category':[('DimDate','YearMonth')],'Y':M('Net Incremental Promotion Profit')})]),
          ('Innovation Performance','Which launches are working?', ['Innovation Revenue','Innovation Contribution %','Cohort Repeat Rate %','Target Attainment %'],[
           ('lineChart','Launch trajectory',{'Category':[('DimDate','YearMonth')],'Series':[('DimProduct','Product')],'Y':M('Innovation Revenue')}),
           ('scatterChart','Launch reach and demand',{'Category':[('DimProduct','Product')],'X':M('Distribution %'),'Y':M('Velocity'),'Size':M('Innovation Revenue')}),
           ('tableEx','Post-launch review',{'Values':[('DimProduct','Product'),('DimProduct','LaunchDate')]+M('Innovation Revenue','Velocity','Distribution %','Cohort Repeat Rate %','Gross Margin %','Target Attainment %')}),
           ('clusteredBarChart','Repeat among complete trial cohorts',{'Category':[('DimProduct','Product')],'Y':M('Cohort Repeat Rate %')})]),
          ('Opportunity Finder','Why did performance change?', ['Revenue vs Target','Gross Margin %','Velocity','Distribution Opportunity Revenue'],[
           ('decompositionTreeVisual','Investigate the plan gap',{'Values':M('Revenue vs Target'),'ExplainBy':[('DimCategory','Category'),('DimChannel','Channel'),('DimRegion','Region'),('DimProduct','Product')]}),
           ('clusteredBarChart','Selected KPI by analysis axis',{'Category':[('DimCategory','Category')],'Y':M('Selected KPI')}),
           ('tableEx','Distribution scenario candidates',{'Values':[('DimProduct','Product')]+M('Revenue','Distribution %','Velocity','Gross Margin %','Distribution Opportunity Revenue')}),
           ('card','Selected KPI',{'Values':M('Selected KPI')})]),
          ('Executive Action Centre','What should we test next?', [],[
           ('tableEx','FY2024 generated action hypotheses; fixed snapshot scope',{'Values':[('ActionCentre',c) for c in ['Observation','Driver','Implication','Action','Monitor']]}),
           ('tableEx','Public CCEP Group context; independent of simulation',{'Values':[('PublicContext',c) for c in ['Metric','Value','Basis','Scope']]}),
           ('textbox','Actions are hypotheses derived from synthetic data. No realised company outcomes. Refresh the Python pipeline to regenerate the FY2024 snapshot.',{}),
           ('textbox','Public CCEP Group growth is shown separately and does not validate fictional SKU/customer performance.',{})])]
    return [
      ('Championship Command Centre','How did the championship develop?', ['Total Recorded Points','Wins','Podiums','Non-finishes','Average Qualifying Position','Points per Start'],[
       ('clusteredBarChart','Recorded driver points (GP + sprint)',{'Category':[('DimDriver','Driver')],'Y':M('Total Recorded Points')}),
       ('lineChart','GP-only points progression',{'Category':[('DimRace','Round')],'Series':[('DimDriver','Driver')],'Y':M('Cumulative GP Points')}),
       ('clusteredBarChart','Official constructor points',{'Category':[('DimConstructor','Constructor')],'Y':M('Official Constructor Points')}),
       ('tableEx','Championship and execution',{'Values':[('DimDriver','Driver')]+M('Total Recorded Points','Wins','Podiums','Non-finishes')})]),
      ('Driver Intelligence','Who converts opportunity into results?', ['Starts','Classified Position Gain','Movement Eligible Starts','Non-finish Rate %'],[
       ('clusteredBarChart','Classified position gain',{'Category':[('DimDriver','Driver')],'Y':M('Classified Position Gain')}),
       ('scatterChart','Qualifying and points per start',{'Category':[('DimDriver','Driver')],'X':M('Average Qualifying Position'),'Y':M('Points per Start'),'Size':M('Starts')}),
       ('tableEx','Driver comparison and sample sizes',{'Values':[('DimDriver','Driver')]+M('Average Qualifying Position','Average Finish','Classified Position Gain','Movement Eligible Starts','Teammate Comparable Starts','Teammate Ahead Rate %','Non-finishes')}),
       ('clusteredBarChart','Ahead of teammate; shared completed races',{'Category':[('DimDriver','Driver')],'Y':M('Teammate Ahead Rate %')})]),
      ('Constructor Performance','Where do points and non-finishes concentrate?', ['Total Recorded Points','Points per Start','Non-finish Rate %','Median Pit Duration'],[
       ('clusteredBarChart','Constructor recorded points',{'Category':[('DimConstructor','Constructor')],'Y':M('Total Recorded Points')}),
       ('clusteredBarChart','All-cause non-finishes',{'Category':[('DimConstructor','Constructor')],'Y':M('Non-finish Rate %')}),
       ('tableEx','Constructor execution',{'Values':[('DimConstructor','Constructor')]+M('Average Qualifying Position','Points per Start','Classified Position Gain','Non-finishes','Median Pit Duration')}),
       ('clusteredBarChart','Driver points contribution',{'Category':[('DimDriver','Driver')],'Series':[('DimConstructor','Constructor')],'Y':M('Total Recorded Points')})]),
      ('Circuit Intelligence','Where do observed results differ?', ['Starts','Classified Position Gain','Non-finish Rate %','Median Pit Duration'],[
       ('clusteredBarChart','Observed position movement by circuit',{'Category':[('DimCircuit','Circuit')],'Y':M('Classified Position Gain')}),
       ('clusteredBarChart','Non-finishes by circuit',{'Category':[('DimCircuit','Circuit')],'Y':M('Non-finish Rate %')}),
       ('tableEx','Circuit performance history',{'Values':[('DimCircuit','Circuit')]+M('Starts','Classified Position Gain','Non-finish Rate %','Average Qualifying Position','Median Pit Duration')}),
       ('clusteredBarChart','Circuit points concentration',{'Category':[('DimCircuit','Circuit')],'Y':M('GP Points')})]),
      ('Strategy Evidence','Observed pit windows; no compound telemetry', ['Pit Stops','Median Pit Window','Sample Lap Observations','Median Sample Lap'],[
       ('clusteredColumnChart','Recorded pit window by race',{'Category':[('DimRace','Race')],'Y':M('Median Pit Window')}),
       ('lineChart','Sample raw lap times: Bahrain / Monaco 2024',{'Category':[('FactLaps','Lap')],'Series':[('DimDriver','Driver')],'Y':M('Median Sample Lap')}),
       ('tableEx','Observed stop sequence',{'Values':[('DimRace','Race'),('DimDriver','Driver'),('FactPitStops','Stop'),('FactPitStops','Lap'),('FactPitStops','DurationSeconds')]}),
       ('textbox','No tyre compounds, weather or telemetry supplied. Lap samples include traffic and interruptions. No degradation, undercut or clean-air-pace inference.',{})]),
      ('Pit Stop Performance','How consistent are recorded pit durations?', ['Pit Stops','Eligible Pit Stops','Median Pit Duration','Pit Duration StdDev'],[
       ('clusteredBarChart','Eligible duration median by constructor',{'Category':[('DimConstructor','Constructor')],'Y':M('Median Pit Duration')}),
       ('clusteredBarChart','Duration dispersion',{'Category':[('DimConstructor','Constructor')],'Y':M('Pit Duration StdDev')}),
       ('tableEx','Audit all observed stops',{'Values':[('DimRace','Race'),('DimDriver','Driver'),('FactPitStops','Lap'),('FactPitStops','DurationSeconds'),('FactPitStops','TimingEligible')]}),
       ('textbox','Duration is the API pit-duration field, not stationary wheel-change time. Compare within a race. The 10–60 second screen retains excluded rows for audit.',{})]),
      ('Qualifying vs Race Execution','Who improves relative to their starting grid?', ['Average Grid','Average Finish','Classified Position Gain','GP Points Above Grid Benchmark'],[
       ('scatterChart','Grid vs finishing classification',{'Category':[('DimDriver','Driver')],'X':M('Average Grid'),'Y':M('Average Finish'),'Size':M('Starts')}),
       ('clusteredBarChart','Points above grid benchmark',{'Category':[('DimConstructor','Constructor')],'Y':M('GP Points Above Grid Benchmark')}),
       ('tableEx','Execution with survivorship context',{'Values':[('DimDriver','Driver')]+M('Classified Position Gain','Movement Eligible Starts','Starts','Non-finishes','GP Points Above Grid Benchmark')}),
       ('clusteredBarChart','Observed qualifying result',{'Category':[('DimDriver','Driver')],'Y':M('Average Qualifying Position')})]),
      ('Strategy Lab','SIMULATION: explore assumption sensitivity', ['Scenario Pit Cost','Scenario Degradation Cost','Scenario Added Time'],[
       ('lineChart','Added time across assumed stop counts',{'Category':[('StopCount','Value')],'Y':M('Scenario Added Time')}),
       ('tableEx','Simulation cost components',{'Values':[('StopCount','Value')]+M('Scenario Pit Cost','Scenario Degradation Cost','Scenario Added Time')}),
       ('textbox','SIMULATION. Equal integer stints; linear assumed degradation reset by each stop; constant assumed pit loss. Excludes traffic, fuel, safety cars, compounds and overtaking.',{}),
       ('textbox','Outputs are extra elapsed-time assumptions relative to a constant fresh-tyre baseline. They are not race predictions or observed telemetry.',{})])]

def build_report(domain,label):
    palette=COLORS[domain]
    report=ROOT/'powerbi'/f'{label}.Report'
    definition=report/'definition'
    if definition.exists(): shutil.rmtree(definition)
    page_specs=specs(domain)
    page_names=[f'{domain}_{i+1:02d}' for i in range(8)]
    write_json({'$schema':schema('pbip/pbipProperties/1.0.0'),'version':'1.0','artifacts':[{'report':{'path':label+'.Report'}}],'settings':{'enableAutoRecovery':True}},ROOT/'powerbi'/(label+'.pbip'))
    write_json({'$schema':schema('item/report/definitionProperties/2.0.0'),'version':'4.0','datasetReference':{'byPath':{'path':'../'+label+'.SemanticModel'}}},report/'definition.pbir')
    write_json({'$schema':schema('item/report/definition/versionMetadata/1.0.0'),'version':'4.0.0'},definition/'version.json')
    write_json({'$schema':schema('item/report/definition/report/2.0.0'),'themeCollection':{},
                'filterConfig':filter_config('DimDate' if domain=='fmcg' else 'DimSeason','Year' if domain=='fmcg' else 'Season',2024),
                'settings':{'useStylableVisualContainerHeader':True}},definition/'report.json')
    inventory=[]
    for i,(title,question,kpis,charts) in enumerate(page_specs):
        page_name=page_names[i]
        page={'$schema':schema('item/report/definition/page/2.0.0'),'name':page_name,'displayName':title,
              'displayOption':'FitToPage','width':1440,'height':900,'objects':{'background':obj(color=fill(palette['bg']),transparency=lit(0))}}
        if domain=='fmcg' and i==5:
            page['filterConfig']=filter_config('DimProduct','Innovation',1)
        if domain=='f1' and i==7:
            # Keep the stop-count curve/table comparable while the selector
            # changes the current-scenario cards. Other assumptions still filter.
            page['visualInteractions']=[{'source':'control_0','target':target,'type':'NoFilter'} for target in ['chart_0','chart_1']]
        path=definition/'pages'/page_name
        write_json(page,path/'page.json')
        visuals=[textbox('header','APEX INSIGHTS  /  '+title,224,22,1180,45,palette,24),
                 textbox('question',question,224,72,1170,30,palette,13),
                 textbox('brand','APEX\nINSIGHTS',20,24,180,70,palette,20)]
        provenance='ALL COMMERCIAL METRICS SYNTHETIC · AUD ex GST · FY2024 default; change year in Filters pane' if domain=='fmcg' else 'PUBLIC: Jolpica-F1 / Ergast · CC BY-NC-SA 4.0 · 2024 default; change season in Filters pane'
        if domain=='f1' and i==7:
            provenance='SIMULATION · ASSUMED INPUTS · NOT TELEMETRY · NO REAL RACE OUTCOME PREDICTION'
        visuals.append(textbox('provenance',provenance,224,850,1170,36,palette,10))
        for j,name in enumerate(page_names):
            button=visual('nav_'+str(j),'actionButton',16,140+j*68,190,56,f'{j+1:02d}  '+page_specs[j][0],{},palette)
            button['visual']['visualContainerObjects']['visualLink']=obj(show=lit(True),type=lit('PageNavigation'),navigationSection=lit(name))
            button['visual']['visualContainerObjects']['title'][0]['properties']['fontSize']=lit(10)
            visuals.append(button)
        no_filters=domain=='fmcg' and i==7 or domain=='f1' and i==7
        slicers=[] if no_filters else [('DimCategory','Category'),('DimChannel','Channel'),('DimRegion','Region')] if domain=='fmcg' else [('DimDriver','Driver'),('DimConstructor','Constructor'),('DimRace','Race')]
        for j,s in enumerate(slicers):
            v=visual('slicer_'+s[0],'slicer',224+j*392,110,376,66,s[1],{'Values':[s]},palette,{'data':obj(mode=lit('Dropdown'))})
            # Championship race slicer is excluded from sync group because official standings don't respond.
            v['visual']['syncGroup']={'groupName':domain+'_'+s[0],'fieldChanges':True,'filterChanges':True}
            visuals.append(v)
        for j,kpi in enumerate(kpis):
            width=(1176-16*(len(kpis)-1))/len(kpis)
            visuals.append(visual('kpi_'+str(j),'card',224+j*(width+16),194,width,108,kpi,{'Values':[('Measures',kpi)]},palette))
        for j,(kind,chart_title,roles) in enumerate(charts):
            x,y=224+(j%2)*596,326+(j//2)*252
            if kind=='textbox':
                v=textbox('chart_'+str(j),chart_title,x,y,578,228,palette,14)
            else:
                v=visual('chart_'+str(j),kind,x,y,578,228,chart_title,roles,palette)
            if domain=='fmcg' and i==0 and j==2:
                v['visual']['objects'].setdefault('dataPoint',obj(defaultColor={'solid':{'color':{'expr':measure('Variance Colour')}}}))
                v['visual']['objects']['dataPoint']=obj(defaultColor={'solid':{'color':{'expr':measure('Variance Colour')}}})
            if domain=='fmcg' and i==6 and j==1:
                v['visual']['query']['queryState']['Category']['fieldParameters']=[{'parameterExpr':col('AnalysisAxis','Axis'),'index':0,'length':1}]
                v['visual']['visualContainerObjects']['title']=obj(show=lit(True),text={'expr':measure('Dynamic Title')},fontColor=fill(palette['ink']))
            if kind in ['scatterChart','clusteredBarChart','lineChart'] and not (domain=='f1' and i==7):
                v['visual']['visualContainerObjects']['visualTooltip']=obj(show=lit(True),type=lit('ReportPage'),section=lit(domain+'_tooltip'))
            visuals.append(v)
        if domain=='fmcg' and i==6:
            # Overlay controls in the top slicer band; offsets stay inside canvas.
            for j,s in enumerate([('KPISelector','KPI'),('AnalysisAxis','Axis'),('DistributionGoal','Value')]):
                visuals.append(visual('control_'+str(j),'slicer',224+j*392,110,376,66,s[0],{'Values':[s]},palette))
            visuals=[v for v in visuals if not v['name'].startswith('slicer_')]
        if domain=='f1' and i==7:
            for j,s in enumerate([('StopCount','Value'),('PitLoss','Value'),('Degradation','Value'),('RaceLaps','Value')]):
                visuals.append(visual('control_'+str(j),'slicer',224+j*294,110,278,66,s[0],{'Values':[s]},palette,{'selection':obj(singleSelect=lit(True))}))
        if domain=='fmcg' and i==7:
            # A broad five-column action matrix needs the width, not a small tile.
            for v in visuals:
                if v['name']=='chart_0': v['position'].update(x=224,y=160,width=1176,height=370)
                if v['name']=='chart_1': v['position'].update(x=224,y=548,width=1176,height=150)
                if v['name']=='chart_2': v['position'].update(x=224,y=710,width=578,height=118)
                if v['name']=='chart_3': v['position'].update(x=820,y=710,width=578,height=118)
        for z,v in enumerate(visuals):
            v['position']['z']=z; v['position']['tabOrder']=z
            write_json(v,path/'visuals'/v['name']/'visual.json')
        inventory.append(dict(domain=domain,page=title,question=question,visuals=len(visuals),status='AUTHORED_SOURCE; Desktop runtime pending'))
    # Genuine native tooltip and drillthrough definitions; runtime QA pending.
    for kind in ['tooltip','detail']:
        pname=domain+'_'+kind
        table,column=('DimProduct','Product') if domain=='fmcg' else ('DimDriver','Driver')
        typ='Tooltip' if kind=='tooltip' else 'Drillthrough'
        page={'$schema':schema('item/report/definition/page/2.0.0'),'name':pname,'displayName':typ+' detail',
              'displayOption':'FitToPage','width':600 if kind=='tooltip' else 1440,'height':360 if kind=='tooltip' else 900,
              'type':typ,'visibility':'HiddenInViewMode','pageBinding':{'name':domain+'_'+kind+'_binding','type':typ,
              'parameters':[{'name':domain+'_'+kind+'_context','fieldExpr':col(table,column),'boundFilter':domain+'_'+kind+'_filter'}]},
              'filterConfig':{'filters':[{'name':domain+'_'+kind+'_filter','type':'Categorical','field':col(table,column),'howCreated':'Drillthrough' if kind=='detail' else 'User'}]},
              'objects':{'background':obj(color=fill(palette['bg']),transparency=lit(0))}}
        path=definition/'pages'/pname
        write_json(page,path/'page.json')
        ms=['Revenue','Gross Margin %','Velocity','Distribution %'] if domain=='fmcg' else ['Total Recorded Points','Classified Position Gain','Movement Eligible Starts','Non-finishes']
        if kind=='tooltip':
            v=visual('detail_table','tableEx',20,70,560,240,'SYNTHETIC detail' if domain=='fmcg' else 'PUBLIC_DERIVED detail',{'Values':[(table,column)]+[('Measures',m) for m in ms]},palette)
        else:
            v=visual('detail_table','tableEx',40,130,1360,660,'Drillthrough context and denominator',{'Values':[(table,column)]+[('Measures',m) for m in ms]},palette)
        write_json(v,path/'visuals'/v['name']/'visual.json')
        write_json(textbox('header',('SYNTHETIC' if domain=='fmcg' else 'PUBLIC_DERIVED')+' / '+typ+' detail',20,20,560,44,palette,16),path/'visuals/header/visual.json')
    write_json({'$schema':schema('item/report/definition/pagesMetadata/1.0.0'),'pageOrder':page_names+[domain+'_tooltip',domain+'_detail'],'activePageName':page_names[0]},definition/'pages/pages.json')
    bookmark='executive_view'
    write_json({'$schema':schema('item/report/definition/bookmarksMetadata/1.0.0'),'items':[{'name':bookmark}]},definition/'bookmarks/bookmarks.json')
    write_json({'$schema':schema('item/report/definition/bookmark/1.0.0'),'name':bookmark,'displayName':'Executive view',
                'options':{'suppressData':True,'suppressDisplay':True,'suppressActiveSection':False},
                'explorationState':{'version':'1.3','activeSection':page_names[0],'sections':{}}},definition/'bookmarks'/f'{bookmark}.bookmark.json')
    theme={'name':'APEX '+label,'dataColors':[palette['accent'],'#6485A0','#CBA36F','#8B739E','#618E85'],
           'background':palette['bg'],'foreground':palette['ink'],'tableAccent':palette['accent'],
           'textClasses':{'title':{'fontFace':'Segoe UI','fontSize':14,'color':palette['ink']},'label':{'fontFace':'Segoe UI','fontSize':11,'color':palette['ink']}}}
    write_json(theme,ROOT/'powerbi/themes'/(label+'.json'))
    return inventory

def main():
    inventory=[]
    for domain,label in [('fmcg','Commercial'),('f1','Motorsport')]:
        build_model(domain,label)
        inventory+=build_report(domain,label)
    write_json(inventory,ROOT/'outputs/report_inventory.json')
    doc='# DAX measure library\n\nThese measures exist in the native `model.bim` files. Source authored; runtime evaluation pending Windows acceptance.\n\n'
    for domain,library in [('Commercial — ALL SYNTHETIC',FMCG),('F1 — PUBLIC_DERIVED; Strategy Lab SIMULATION',F1)]:
        doc+='## '+domain+'\n\n'
        for item in library:
            doc+='### '+item['name']+'\n\n'+item['description']+'\n\n```dax\n'+item['name']+' =\n'+item['expression']+'\n```\n\n'
    (ROOT/'powerbi/dax_measures.md').write_text(doc.rstrip()+'\n')
    print('Authored two native PBIP projects:',len(FMCG)+len(F1),'measures;',len(inventory),'visible pages + 4 utility pages')

if __name__=='__main__': main()
