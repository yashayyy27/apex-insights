"""Offline Microsoft schema validation plus model/visual referential checks.

This deliberately does NOT call schema success a Power BI runtime test.
"""
import json
from pathlib import Path
import jsonschema
from referencing import Registry,Resource
from referencing.jsonschema import DRAFT7
from common import ROOT,write_json,sha256

def main():
    p=ROOT/'powerbi/schemas'
    manifest=json.loads((p/'manifest.json').read_text())
    store={}
    for url,meta in manifest.items():
        if sha256(p/meta['file'])!=meta['sha256']:
            raise ValueError('Modified schema '+url)
        value=json.loads((p/meta['file']).read_text())
        store[url]=value
        if '$id' in value: store[value['$id']]=value
    errors=[];count=0;bindings=0
    registry=Registry().with_resources([(url,Resource.from_contents(value,default_specification=DRAFT7)) for url,value in store.items()])
    for file in sorted((ROOT/'powerbi').rglob('*.json'))+sorted((ROOT/'powerbi').glob('*.pbip'))+sorted((ROOT/'powerbi').rglob('*.pbir'))+sorted((ROOT/'powerbi').rglob('*.pbism')):
        if 'schemas' in file.parts or 'themes' in file.parts: continue
        value=json.loads(file.read_text())
        url=value.get('$schema')
        if not url: continue
        sch=store[url]
        validator=jsonschema.Draft7Validator(sch,registry=registry)
        for e in validator.iter_errors(value):
            errors.append(dict(file=str(file.relative_to(ROOT)),path='.'.join(map(str,e.path)),message=e.message))
        count+=1
    for label in ['Commercial','Motorsport']:
        model=json.loads((ROOT/f'powerbi/{label}.SemanticModel/model.bim').read_text())['model']
        tables={t['name']:t for t in model['tables']}
        for r in model['relationships']:
            for side in ['from','to']:
                assert r[side+'Table'] in tables
                assert r[side+'Column'] in {c['name'] for c in tables[r[side+'Table']]['columns']}
            assert r['crossFilteringBehavior']=='oneDirection'
        def walk(value,file):
            nonlocal bindings
            if isinstance(value,dict):
                for key,val in value.items():
                    if key in ['Column','Measure'] and isinstance(val,dict) and 'Expression' in val:
                        entity=val['Expression'].get('SourceRef',{}).get('Entity')
                        if entity:
                            if entity not in tables:
                                errors.append(dict(file=str(file),message='Unknown table '+entity))
                            else:
                                names={x['name'] for x in tables[entity].get('measures' if key=='Measure' else 'columns',[])}
                                if val['Property'] not in names: errors.append(dict(file=str(file),message='Unknown field '+entity+'.'+val['Property']))
                            bindings+=1
                    walk(val,file)
            elif isinstance(value,list):
                for val in value: walk(val,file)
        report=ROOT/f'powerbi/{label}.Report/definition'
        pages=json.loads((report/'pages/pages.json').read_text())['pageOrder']
        for page in pages:
            assert (report/'pages'/page/'page.json').exists()
            page_root=report/'pages'/page
            page_definition=json.loads((page_root/'page.json').read_text())
            visual_names={json.loads(p.read_text())['name'] for p in page_root.rglob('visual.json')}
            for interaction in page_definition.get('visualInteractions',[]):
                assert interaction['source'] in visual_names and interaction['target'] in visual_names
        for file in report.rglob('visual.json'):
            value=json.loads(file.read_text()); walk(value,file.relative_to(ROOT))
            pos=value['position']; page=json.loads((file.parents[2]/'page.json').read_text())
            assert pos['x']>=0 and pos['y']>=0 and pos['x']+pos['width']<=page['width'] and pos['y']+pos['height']<=page['height'],str(file)
        # Machine-dependent source paths stay in one parameter, not every partition.
        for table in model['tables']:
            for partition in table['partitions']:
                expr=partition['source']['expression']
                assert '/Users/' not in expr and 'C:/' not in expr
    report=dict(status='PASS' if not errors else 'FAIL',schema_files_validated=count,field_bindings_checked=bindings,
                errors=errors,desktop_open='NOT_TESTED',dax_execution='NOT_TESTED',m_refresh='NOT_TESTED',interactions='NOT_TESTED')
    write_json(report,ROOT/'outputs/powerbi_source_validation.json')
    print(json.dumps(report,indent=2))
    if errors: raise AssertionError('Power BI source validation failed')

if __name__=='__main__': main()
