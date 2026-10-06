/** Native formula-driven management workbook. Requires @oai/artifact-tool. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const input=JSON.parse(await fs.readFile(path.join(here,'management_inputs.json'),'utf8'));
const wb=Workbook.create();
const names=['Executive Summary','Category Performance','Customer Channel','Innovation','Scenario Analysis','Monthly Inputs','SKU Inputs','Launch Inputs','Methodology'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const dark='#172B3A',accent='#AD3045',muted='#526777',pale='#F2F5F8';
const money='$#,##0;($#,##0);$0',pct='0.0%;-0.0%;0.0%';
function base(s,title,scope,range='A1:O48'){
  s.showGridLines=false;
  s.getRange(range).format.font={name:'Arial',size:10,color:dark};
  s.getRange(range).format.rowHeight=23;
  s.getRange(range).format.columnWidth=16;
  s.getRange(range).format.verticalAlignment='center';
  s.getRange('A2').values=[[title]];
  s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:dark};
  s.getRange('A3').values=[[scope]];
  s.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:muted};
  s.getRange('A4:O4').format.borders={bottom:{style:'thin',color:'#B7C4CF'}};
}
function header(s,range){s.getRange(range).format={fill:dark,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:29};}
function table(s,headers,rows,row=5,name=null){
  const cols=headers.length;
  s.getRangeByIndexes(row-1,0,1,cols).values=[headers];
  s.getRangeByIndexes(row,0,rows.length,cols).values=rows;
  header(s,`A${row}:${String.fromCharCode(64+cols)}${row}`);
  if(name){const t=s.tables.add(`A${row}:${String.fromCharCode(64+cols)}${row+rows.length}`,true,name);t.style='TableStyleLight1';}
}
function chart(s,type,ranges,title,from,to,format=money){
  const c=s.charts.add(type,ranges.length===1?s.getRange(ranges[0]):ranges.map(r=>s.getRange(r)));
  c.title=title;c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=13;
  c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:10}};
  c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
  c.yAxis={numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
  c.setPosition(from,to);
  c.series.items.forEach((series,i)=>{series.fill=i===0?accent:'#6485A0';if(type==='line')series.line={fill:i===0?accent:'#6485A0',style:i===0?'solid':'dashed',width:2};});
  return c;
}

// Inputs own original aggregated values, outputs own calculation logic.
const monthly=sheets['Monthly Inputs'];
base(monthly,'Monthly commercial inputs','SYNTHETIC. Monthly category/channel/region totals, AUD ex GST. Generator seed 20261006.','A1:I26');
const monthlyCols=['Year','YearMonth','Category','Channel','Region','Revenue','Units','GrossProfit','TargetRevenue'];
table(monthly,monthlyCols,input.monthly.map(r=>monthlyCols.map(c=>r[c])),5,'MonthlyCommercialInputs');
const end=5+input.monthly.length;
monthly.getRange(`F6:F${end}`).setNumberFormat(money);monthly.getRange(`H6:I${end}`).setNumberFormat(money);monthly.getRange(`G6:G${end}`).setNumberFormat('#,##0');
monthly.getRange(`A5:I${end}`).format.columnWidth=19;monthly.getRange(`C5:D${end}`).format.columnWidth=22;
monthly.freezePanes.freezeRows(5);
const sku=sheets['SKU Inputs'];
base(sku,'SKU scenario inputs','SYNTHETIC. FY2024 source totals from sku_productivity SQL view.','A1:H35');
const skuHeaders=['ProductKey','Product','Revenue','Units','GrossProfit','ActiveStoreDays','EligibleStoreDays','Distribution'];
table(sku,skuHeaders,input.sku.map(r=>skuHeaders.map(c=>r[c])),5,'SkuScenarioInputs');
sku.getRange('B5:B29').format.columnWidth=35;sku.getRange('C6:C29').setNumberFormat(money);sku.getRange('E6:E29').setNumberFormat(money);sku.getRange('D6:D29').setNumberFormat('#,##0');sku.getRange('F6:G29').setNumberFormat('#,##0');sku.getRange('H6:H29').setNumberFormat(pct);
sku.freezePanes.freezeRows(5);
const launch=sheets['Launch Inputs'];
base(launch,'Launch review inputs','SYNTHETIC. Cohorts require complete 28-day follow-up; sales from launch to 31 Dec 2024.','A1:K22');
const launchHeaders=['ProductKey','Product','Revenue','Units','GrossProfit','Velocity','Distribution','TargetAttainment','Trials','Repeats'];
table(launch,launchHeaders,input.innovation.map(r=>launchHeaders.map(c=>r[c])),5,'LaunchReviewInputs');
launch.getRange('B5:B7').format.columnWidth=35;launch.getRange('C6:C7').setNumberFormat(money);launch.getRange('E6:E7').setNumberFormat(money);launch.getRange('G6:H7').setNumberFormat(pct);launch.getRange('F6:F7').setNumberFormat('0.00');
launch.getRange('D6:D7').setNumberFormat('#,##0');launch.getRange('I6:J7').setNumberFormat('#,##0');

const exec=sheets['Executive Summary'];
base(exec,'APEX commercial management pack','ALL PERFORMANCE SYNTHETIC. Fictional beverage portfolio, AUD ex GST.');
exec.tabColor=dark;
exec.getRange('A5').values=[['Reporting year']];exec.getRange('B5').values=[[2024]];exec.getRange('B5').format.fill='#FFF0C2';exec.getRange('B5').dataValidation={rule:{type:'list',values:['2023','2024']}};
exec.getRange('A7:C7').values=[['Metric','Result','Interpretation']];header(exec,'A7:C7');
exec.getRange('A8:A13').values=[['Net revenue'],['Gross profit'],['Gross margin'],['Target attainment'],['Revenue YoY'],['Units']];
exec.getRange('B8:B13').formulas=[
 [`=SUMIFS('Monthly Inputs'!$F$6:$F$${end},'Monthly Inputs'!$A$6:$A$${end},$B$5)`],
 [`=SUMIFS('Monthly Inputs'!$H$6:$H$${end},'Monthly Inputs'!$A$6:$A$${end},$B$5)`],
 ['=B9/B8'],
 [`=B8/SUMIFS('Monthly Inputs'!$I$6:$I$${end},'Monthly Inputs'!$A$6:$A$${end},$B$5)`],
 [`=IF($B$5=2023,"n.a.",B8/SUMIFS('Monthly Inputs'!$F$6:$F$${end},'Monthly Inputs'!$A$6:$A$${end},$B$5-1)-1)`],
 [`=SUMIFS('Monthly Inputs'!$G$6:$G$${end},'Monthly Inputs'!$A$6:$A$${end},$B$5)`]];
exec.getRange('C8:C13').values=[['Before trade spend'],['Before overheads/trade spend'],['Ratio of total GP / revenue'],['Independent plan baseline'],['Matching prior calendar year'],['Individual beverage packs']];
exec.getRange('A7:A13').format.columnWidth=24;exec.getRange('B7:B13').format.columnWidth=22;exec.getRange('C7:C13').format.columnWidth=34;
exec.getRange('B8:B9').setNumberFormat(money);exec.getRange('B10:B12').setNumberFormat(pct);exec.getRange('B13').setNumberFormat('#,##0');
exec.getRange('A16:D16').values=[['Month','Revenue','Target','Variance']];header(exec,'A16:D16');
for(let i=0;i<12;i++){
  const r=17+i;
  exec.getRange(`A${r}`).formulas=[[`=TEXT(DATE($B$5,${i+1},1),"yyyy-mm")`]];
  exec.getRange(`B${r}`).formulas=[[`=SUMIFS('Monthly Inputs'!$F$6:$F$${end},'Monthly Inputs'!$B$6:$B$${end},A${r})`]];
  exec.getRange(`C${r}`).formulas=[[`=SUMIFS('Monthly Inputs'!$I$6:$I$${end},'Monthly Inputs'!$B$6:$B$${end},A${r})`]];
  exec.getRange(`D${r}`).formulas=[[`=B${r}-C${r}`]];
}
exec.getRange('B17:D28').setNumberFormat(money);
exec.getRange('D17:D28').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:accent,bold:true}}});
chart(exec,'line',['A16:C28'],'Monthly revenue and plan (AUD)','F7','O28');
exec.getRange('A31').values=[['FY2024 action hypotheses (fixed snapshot)']];exec.getRange('A31').format.font.bold=true;
input.actions.slice(0,3).forEach((a,i)=>{const row=33+i*3;exec.mergeCells(`A${row}:O${row+1}`);exec.getRange(`A${row}`).values=[[a.Observation+'. '+a.Action+'. Monitor: '+a.Monitor+'.']];exec.getRange(`A${row}:O${row+1}`).format.wrapText=true;});

const category=sheets['Category Performance'];base(category,'Category economics','SYNTHETIC. Calendar year selected on Executive Summary.');category.tabColor=dark;
category.getRange('A5').values=[['Year']];category.getRange('B5').formulas=[["='Executive Summary'!B5"]];
table(category,['Category','Revenue','Units','Gross profit','GP margin','Target','Attainment','Revenue LY','YoY'],input.categories.map(r=>[r.Category,null,null,null,null,null,null,null,null]),7);
for(let r=8;r<=12;r++){
  for(const [dest,src] of [['B','F'],['C','G'],['D','H'],['F','I']])category.getRange(`${dest}${r}`).formulas=[[`=SUMIFS('Monthly Inputs'!$${src}$6:$${src}$${end},'Monthly Inputs'!$C$6:$C$${end},$A${r},'Monthly Inputs'!$A$6:$A$${end},$B$5)`]];
  category.getRange(`E${r}`).formulas=[[`=D${r}/B${r}`]];category.getRange(`G${r}`).formulas=[[`=B${r}/F${r}`]];
  category.getRange(`H${r}`).formulas=[[`=SUMIFS('Monthly Inputs'!$F$6:$F$${end},'Monthly Inputs'!$C$6:$C$${end},$A${r},'Monthly Inputs'!$A$6:$A$${end},$B$5-1)`]];
  category.getRange(`I${r}`).formulas=[[`=IF(H${r}=0,"n.a.",B${r}/H${r}-1)`]];
}
for(const c of ['B','D','F','H'])category.getRange(`${c}8:${c}12`).setNumberFormat(money);
category.getRange('C8:C12').setNumberFormat('#,##0');
for(const c of ['E','G','I'])category.getRange(`${c}8:${c}12`).setNumberFormat(pct);
category.getRange('G8:G12').conditionalFormats.add('cellIs',{operator:'lessThan',formula:1,format:{font:{color:accent,bold:true}}});
chart(category,'bar',['A7:B12'],'Category revenue (AUD)','A16','I33');

const channel=sheets['Customer Channel'];base(channel,'Customer and channel performance','SYNTHETIC. One fictional account per channel/region combination.','A1:K43');channel.tabColor=dark;
channel.getRange('A5').values=[['Year']];channel.getRange('B5').formulas=[["='Executive Summary'!B5"]];
const channels=['Grocery','Convenience','Petrol','Hospitality','Independent retail'];const regions=['NSW','VIC','QLD'];
table(channel,['Account','Channel','Region','Revenue','Units','GP margin','Target','Attainment','YoY'],channels.flatMap((c,i)=>regions.map((reg,j)=>[`Fictional Account ${String(i+1).padStart(2,'0')}-${j+1}`,c,reg,null,null,null,null,null,null])),7);
for(let r=8;r<=22;r++){
  const sum=src=>`SUMIFS('Monthly Inputs'!$${src}$6:$${src}$${end},'Monthly Inputs'!$D$6:$D$${end},$B${r},'Monthly Inputs'!$E$6:$E$${end},$C${r},'Monthly Inputs'!$A$6:$A$${end},$B$5)`;
  channel.getRange(`D${r}`).formulas=[['='+sum('F')]];channel.getRange(`E${r}`).formulas=[['='+sum('G')]];channel.getRange(`F${r}`).formulas=[['='+sum('H')+`/D${r}`]];channel.getRange(`G${r}`).formulas=[['='+sum('I')]];channel.getRange(`H${r}`).formulas=[[`=D${r}/G${r}`]];
  const prev=sum('F').replace('$B$5)','$B$5-1)');channel.getRange(`I${r}`).formulas=[[`=IF($B$5=2023,"n.a.",D${r}/${prev}-1)`]];
}
channel.getRange('A7:A22').format.columnWidth=30;channel.getRange('B7:B22').format.columnWidth=24;
for(const c of ['D','G'])channel.getRange(`${c}8:${c}22`).setNumberFormat(money);for(const c of ['F','H','I'])channel.getRange(`${c}8:${c}22`).setNumberFormat(pct);
channel.getRange('E8:E22').setNumberFormat('#,##0');
channel.getRange('H8:H22').conditionalFormats.add('cellIs',{operator:'lessThan',formula:1,format:{font:{color:accent,bold:true}}});

const innovation=sheets['Innovation'];base(innovation,'Post-launch review','SYNTHETIC. FY2024 launches. Complete-follow-up trial cohorts only.','A1:J35');innovation.tabColor=dark;
table(innovation,['Product','Revenue','Velocity','Distribution','Attainment','Trials','Repeat rate','GP margin'],input.innovation.map(r=>[r.Product,null,null,null,null,null,null,null]),7);
innovation.getRange('A7:A9').format.columnWidth=38;
for(let r=8;r<=9;r++){
  const source=r-2;
  innovation.getRange(`B${r}:F${r}`).formulas=[[`='Launch Inputs'!C${source}`,`='Launch Inputs'!F${source}`,`='Launch Inputs'!G${source}`,`='Launch Inputs'!H${source}`,`='Launch Inputs'!I${source}`]];
  innovation.getRange(`G${r}`).formulas=[[`='Launch Inputs'!J${source}/F${r}`]];
  innovation.getRange(`H${r}`).formulas=[[`='Launch Inputs'!E${source}/B${r}`]];
}
innovation.getRange('B8:B9').setNumberFormat(money);innovation.getRange('C8:C9').setNumberFormat('0.00');innovation.getRange('D8:E9').setNumberFormat(pct);innovation.getRange('G8:H9').setNumberFormat(pct);
innovation.getRange('F8:F9').setNumberFormat('#,##0');
chart(innovation,'bar',['A7:A9','G7:G9'],'28-day repeat among complete cohorts','A13','H30',pct);

const scenario=sheets['Scenario Analysis'];base(scenario,'Distribution investment scenario','SIMULATION. FY2024 baseline. No forecast of real CCEP performance.','A1:J42');scenario.tabColor='#6485A0';
scenario.getRange('A6:B10').values=[['Editable assumption','Value'],['SKU key',Number(input.sku[0].ProductKey)],['Target distribution',.70],['Velocity retention',1.0],['Cost per extra SKU-store-day',.10]];header(scenario,'A6:B6');
scenario.getRange('B7:B10').format.fill='#FFF0C2';scenario.getRange('B8:B9').setNumberFormat(pct);scenario.getRange('B10').setNumberFormat('$0.00');scenario.getRange('A6:A33').format.columnWidth=37;scenario.getRange('B6:B33').format.columnWidth=37;
scenario.getRange('B7').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:24}};
scenario.getRange('B8:B9').dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};
scenario.getRange('B10').dataValidation={rule:{type:'decimal',operator:'greaterThanOrEqual',formula1:0}};
scenario.getRange('A13:B13').values=[['FY2024 baseline','Value']];header(scenario,'A13:B13');
scenario.getRange('A14:A22').values=[['Product'],['Revenue'],['Units'],['Gross profit'],['Active SKU-store-days'],['Eligible SKU-store-days'],['Distribution'],['Velocity per active store-day'],['GP per unit']];
for(const [r,c] of [[14,'B'],[15,'C'],[16,'D'],[17,'E'],[18,'F'],[19,'G']])scenario.getRange(`B${r}`).formulas=[[`=_xlfn.XLOOKUP($B$7,'SKU Inputs'!$A$6:$A$29,'SKU Inputs'!$${c}$6:$${c}$29,"Missing SKU",0)`]];
scenario.getRange('B20:B22').formulas=[['=B18/B19'],['=B16/B18'],['=B17/B16']];scenario.getRange('B15').setNumberFormat(money);scenario.getRange('B17').setNumberFormat(money);scenario.getRange('B20').setNumberFormat(pct);scenario.getRange('B21').setNumberFormat('0.00');scenario.getRange('B22').setNumberFormat('$0.00');
scenario.getRange('B16').setNumberFormat('#,##0');scenario.getRange('B18:B19').setNumberFormat('#,##0');
scenario.getRange('A25:B25').values=[['Scenario build','Value']];header(scenario,'A25:B25');
scenario.getRange('A26:A32').values=[['Extra active SKU-store-days'],['Incremental units'],['Net price per unit'],['Incremental revenue'],['Incremental gross profit'],['Incremental distribution cost'],['Contribution after added cost']];
scenario.getRange('B26:B32').formulas=[['=B19*MAX(0,B8-B20)'],['=B26*B21*B9'],['=B15/B16'],['=B27*B28'],['=B27*B22'],['=B26*B10'],['=B30-B31']];
scenario.getRange('B28').setNumberFormat('$0.00');scenario.getRange('B29:B32').setNumberFormat(money);scenario.getRange('B26:B27').setNumberFormat('#,##0');
scenario.getRange('B32').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:accent,bold:true}}});
scenario.mergeCells('D7:J13');scenario.getRange('D7').values=[['Change the amber inputs. The same build recomputes units, revenue and contribution. Assumes constant price/cost and additional distribution. Velocity retention tests demand dilution. No cannibalisation, capacity or supply constraint model.']];scenario.getRange('D7:J13').format.wrapText=true;

const method=sheets['Methodology'];base(method,'Methodology and reconciliation','ALL COMMERCIAL DATA SYNTHETIC. No private corporate data.','A1:H26');
method.getRange('A6:D11').values=[['Input','Source','Scope','Refresh'],['Monthly Inputs','data/processed/analytics/management_monthly.csv','2023–2024 AUD ex GST','Run reproducible pipeline'],['SKU Inputs','sku_productivity SQL view','FY2024 fixed snapshot','Rebuild workbook'],['Launch Inputs','innovation_review SQL view','FY2024, complete repeat cohorts','Rebuild workbook'],['Scenario','User-editable assumptions','Hypothesis only','Live formulas'],['Public CCEP facts','docs/sources.md','Excluded from simulated pack','Separate report context']];header(method,'A6:D6');method.getRange('B6:B11').format.columnWidth=58;method.getRange('C6:C11').format.columnWidth=36;method.getRange('D6:D11').format.columnWidth=30;
method.getRange('A14:B17').values=[['Terminal reconciliation','Residual'],['Category revenue vs executive',null],['Channel revenue vs executive',null],['Monthly detail vs executive',null]];header(method,'A14:B14');
method.getRange('B15:B17').formulas=[["=ROUND(SUM('Category Performance'!B8:B12)-'Executive Summary'!B8,2)"],["=ROUND(SUM('Customer Channel'!D8:D22)-'Executive Summary'!B8,2)"],["=ROUND(SUM('Executive Summary'!B17:B28)-'Executive Summary'!B8,2)"]];method.getRange('B15:B17').setNumberFormat('$0.00');
method.getRange('A14:A17').format.columnWidth=36;
method.getRange('B15:B17').conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{font:{color:accent,bold:true}}});

// Recalculate and independently reconcile, then perturb a live scenario input.
wb.recalculate();
const actual=Number(exec.getRange('B8').values[0][0]);
if(Math.abs(actual-input.metrics.revenue_2024)>.01)throw new Error(`Executive mismatch ${actual}`);
if(Math.abs(Number(exec.getRange('B10').values[0][0])-input.metrics.gross_margin)>1e-10)throw new Error('Margin reconciliation failed');
const before=Number(scenario.getRange('B32').values[0][0]);const baseline=Number(scenario.getRange('B15').values[0][0]);
scenario.getRange('B9').values=[[.80]];wb.recalculate();const after=Number(scenario.getRange('B32').values[0][0]);
if(!(after<before)||Number(scenario.getRange('B15').values[0][0])!==baseline)throw new Error('Scenario perturbation failed');
scenario.getRange('B9').values=[[1.0]];
scenario.getRange('B8').values=[[0]];wb.recalculate();if(Number(scenario.getRange('B32').values[0][0])!==0)throw new Error('Zero distribution expansion boundary failed');scenario.getRange('B8').values=[[.70]];
exec.getRange('B5').values=[[2023]];wb.recalculate();const rev2023=input.monthly.filter(r=>r.Year===2023).reduce((s,r)=>s+r.Revenue,0);
if(Math.abs(Number(exec.getRange('B8').values[0][0])-rev2023)>.01)throw new Error('Year selector failed');exec.getRange('B5').values=[[2024]];
wb.recalculate();
const inspection=await wb.inspect({kind:'table',range:'Executive Summary!A7:C13',include:'values,formulas',tableMaxRows:8,tableMaxCols:3,maxChars:3500});
console.log(inspection.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'final formula error scan'});
if(!errors.ndjson.includes('Cell search matched 0 entries.'))throw new Error('Formula error scan requires inspection: '+errors.ndjson);
await fs.writeFile(path.join(here,'verification.json'),JSON.stringify({engine:'artifact-tool',revenue_reconciled:true,margin_reconciled:true,scenario_perturbation:{before,after,baseline_unchanged:true},year_selector_tested:true,zero_expansion_tested:true,error_scan:errors.ndjson,native_excel_runtime:'NOT_TESTED',pivot_tables:'NOT_CREATED; SUMIFS chosen for auditable export'},null,2));
console.log(errors.ndjson);
await fs.mkdir(path.join(here,'previews'),{recursive:true});
for(const [name,range] of [['Executive Summary','A1:O41'],['Category Performance','A1:I34'],['Customer Channel','A1:I24'],['Innovation','A1:H31'],['Scenario Analysis','A1:J34'],['Monthly Inputs','A1:I20'],['SKU Inputs','A1:H31'],['Launch Inputs','A1:J12'],['Methodology','A1:D19']]){
  const preview=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(here,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(here,'management_pack.xlsx'));
console.log('Saved formula-driven management_pack.xlsx');
