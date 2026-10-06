"""Pin Microsoft's public PBIR JSON schemas for offline structural validation."""
import requests
import json
from urllib.parse import urljoin
from common import ROOT, write_json, sha256

BASE = 'https://developer.microsoft.com/json-schemas/fabric/'
PATHS = [
 'pbip/pbipProperties/1.0.0/schema.json',
 'item/report/definitionProperties/2.0.0/schema.json',
 'item/semanticModel/definitionProperties/1.0.0/schema.json',
 'item/report/definition/versionMetadata/1.0.0/schema.json',
 'item/report/definition/report/2.0.0/schema.json',
 'item/report/definition/pagesMetadata/1.0.0/schema.json',
 'item/report/definition/page/2.0.0/schema.json',
 'item/report/definition/visualContainer/2.1.0/schema.json',
 'item/report/definition/bookmark/1.0.0/schema.json',
 'item/report/definition/bookmarksMetadata/1.0.0/schema.json',
]

def main():
    session = requests.Session()
    manifest = {}
    pending = [BASE + p for p in PATHS]
    while pending:
        url = pending.pop(0)
        if url in manifest:
            continue
        response = session.get(url, timeout=30)
        response.raise_for_status()
        value = response.json()
        name = url.removeprefix(BASE).replace('/', '_')
        path = ROOT / 'powerbi/schemas' / name
        write_json(value, path)
        manifest[url] = {'file': name, 'sha256': sha256(path)}
        def refs(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == '$ref' and isinstance(v, str) and not v.startswith('#'):
                        pending.append(urljoin(url,v).split('#')[0])
                    else:
                        refs(v)
            elif isinstance(obj, list):
                for x in obj:
                    refs(x)
        refs(value)
    write_json(manifest, ROOT / 'powerbi/schemas/manifest.json')
    print('Pinned', len(manifest), 'Microsoft schemas')

if __name__ == '__main__':
    main()
