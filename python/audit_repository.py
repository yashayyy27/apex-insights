"""Audit delivered files, local documentation links and the exported XLSX.

This reads the Open XML package; it does not claim native Excel execution.
"""
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from common import ROOT, sha256, write_json

IGNORED={'.git','.venv','node_modules','__pycache__','.pytest_cache','matplotlib_cache'}
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def main():
    files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in IGNORED for x in p.relative_to(ROOT).parts)
           and p.name!='apex.sqlite' and not p.name.endswith(('.log','.inspect.ndjson'))]
    checks=[]
    def check(name, passed, detail):
        checks.append(dict(check=name,passed=bool(passed),detail=detail))
    required=['README.md','LICENSE','THIRD_PARTY_NOTICES.md','requirements.txt','sql/schema.sql',
              'sql/transformations.sql','sql/analysis_queries.sql','sql/validation_queries.sql',
              'docs/methodology.md','docs/data_dictionary.md','docs/portfolio_case_study.md',
              'docs/interview_guide.md','docs/resume_bullets.md','docs/quality_gate.md',
              'powerbi/Commercial.pbip','powerbi/Motorsport.pbip','powerbi/dax_measures.md',
              'powerbi/power_query.md','powerbi/runtime_acceptance.md','excel/management_pack.xlsx',
              'excel/native_acceptance.md','assets/preview.html']
    check('required_deliverables',all((ROOT/p).is_file() for p in required),required)
    empty=[str(p.relative_to(ROOT)) for p in files if p.stat().st_size==0]
    check('no_empty_deliverables',not empty,empty)
    too_large=[str(p.relative_to(ROOT)) for p in files if p.stat().st_size>=100*1024*1024]
    check('github_file_size_limit',not too_large,too_large)
    bad_json=[]
    for p in files:
        if p.suffix in {'.json','.pbip','.pbir','.pbism','.bim'}:
            try:json.loads(p.read_text())
            except (ValueError,UnicodeError) as exc:bad_json.append([str(p.relative_to(ROOT)),str(exc)])
    check('json_syntax',not bad_json,bad_json)
    missing=[];link_count=0
    for p in files:
        if p.suffix!='.md':continue
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            target=target.strip().split(' "')[0].strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            relative=unquote(target.split('#')[0])
            if not relative:continue
            link_count+=1
            if not (p.parent/relative).exists():missing.append([str(p.relative_to(ROOT)),target])
    check('local_documentation_links',not missing,dict(checked=link_count,missing=missing))
    manifest=json.loads((ROOT/'outputs/processed_manifest.json').read_text())
    changed=[path for path,meta in manifest.items() if sha256(ROOT/path)!=meta['sha256']]
    check('processed_csv_hashes',not changed,dict(files=len(manifest),changed=changed))
    previews=json.loads((ROOT/'outputs/preview_manifest.json').read_text())
    check('reference_preview_provenance',len(previews)==16 and all((ROOT/p['file']).is_file() and p['kind']=='PYTHON_REFERENCE_PREVIEW_NOT_POWER_BI_SCREENSHOT' for p in previews),len(previews))
    with zipfile.ZipFile(ROOT/'excel/management_pack.xlsx') as z:
        names=[s.attrib['name'] for s in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)]
        check('xlsx_nine_sheets',len(names)==9,names)
        forms=[];cached={};errors=[]
        for n in z.namelist():
            if not re.match(r'xl/worksheets/sheet\d+\.xml$',n):continue
            for cell in ET.fromstring(z.read(n)).findall('.//s:c',NS):
                if cell.attrib.get('t')=='e':errors.append([n,cell.attrib['r']])
                formula=cell.find('s:f',NS)
                if formula is not None:
                    forms.append(formula.text or '')
                    cached[(n,cell.attrib['r'])]=cell.findtext('s:v',namespaces=NS)
        check('xlsx_formula_cached_values',len(forms)>200 and all(v is not None for v in cached.values()),dict(formulas=len(forms)))
        check('xlsx_no_cached_errors',not errors,errors)
        check('xlsx_sumifs_xlookup',any('SUMIFS(' in f for f in forms) and any('XLOOKUP(' in f for f in forms),'Functions retained in exported XML')
        charts=[n for n in z.namelist() if re.search(r'/charts/chart\d+\.xml$',n)]
        check('xlsx_three_native_charts',len(charts)==3,charts)
        metrics=json.loads((ROOT/'outputs/insight_metrics.json').read_text())
        revenue=float(cached['xl/worksheets/sheet1.xml','B8'])
        margin=float(cached['xl/worksheets/sheet1.xml','B10'])
        check('xlsx_export_reconciles',abs(revenue-metrics['revenue_2024'])<.01 and abs(margin-metrics['gross_margin'])<1e-10,dict(revenue=revenue,gross_margin=margin))
        check('xlsx_terminal_controls',all(abs(float(cached['xl/worksheets/sheet9.xml',f'B{r}']))<.01 for r in range(15,18)),'All three saved reconciliation residuals = 0')
    verify=json.loads((ROOT/'excel/verification.json').read_text())
    check('excel_runtime_honesty',verify['native_excel_runtime']=='NOT_TESTED','Artifact engine verified; native app acceptance pending')
    qa=json.loads((ROOT/'outputs/powerbi_source_validation.json').read_text())
    check('powerbi_runtime_honesty',all(qa.get(k)=='NOT_TESTED' for k in ['desktop_open','dax_execution','m_refresh','interactions']),qa)
    check('schema_licence_retained',(ROOT/'powerbi/schemas/LICENSE-MICROSOFT.txt').is_file(),'Microsoft MIT licence alongside copied schemas')
    result=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAIL',checks=checks,
                file_count=len(files),total_delivered_bytes=sum(p.stat().st_size for p in files),
                largest_file=str(max(files,key=lambda p:p.stat().st_size).relative_to(ROOT)),
                native_powerbi_runtime='NOT_TESTED',native_excel_runtime='NOT_TESTED')
    write_json(result,ROOT/'outputs/repository_audit.json')
    (ROOT/'docs/repository_audit.md').write_text('# Repository audit\n\nExport/package checks; not native Power BI or Excel certification.\n\n'
        +'| Check | Result |\n|---|---|\n'+''.join(f'| {c["check"]} | {"PASS" if c["passed"] else "FAIL"} |\n' for c in checks)
        +f'\n{len(files)} delivered files; {result["total_delivered_bytes"]/1024/1024:.1f} MiB excluding environment, SQLite build and caches.\n'
        +'\nDetailed evidence: `outputs/repository_audit.json`. Source file size, syntax, links and hashes are checked independently of native runtime.\n')
    print(result['status'],len(checks),'repository/export checks;',len(files),'files')
    if result['status']!='PASS':
        for c in checks:
            if not c['passed']:print(c)
        raise SystemExit(1)

if __name__=='__main__':main()
