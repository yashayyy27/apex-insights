"""Replay offline and compare all supplied processed CSVs byte-for-byte.

After intentional data/generator changes, first rebuild with run_all.py, then
use this command to verify the newly accepted snapshot is reproducible.
"""
import subprocess
import sys
from common import ROOT,sha256,write_json

def hashes():
    return {str(p.relative_to(ROOT)):sha256(p) for p in sorted((ROOT/'data/processed').rglob('*.csv'))}

def main():
    before=hashes()
    if not before:raise ValueError('No processed snapshot to compare; run run_all.py first')
    subprocess.run([sys.executable,str(ROOT/'python/run_all.py')],cwd=ROOT,check=True)
    after=hashes()
    changed=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
    result=dict(status='PASS' if not changed else 'FAIL',mode='offline_cache_replay',
                csv_files_compared=len(before),changed=changed,before=before,after=after,
                scope='Processed CSV content only; no claim of binary XLSX or native Power BI runtime reproducibility')
    write_json(result,ROOT/'outputs/reproducibility_report.json')
    print(result['status'],len(before),'processed CSVs compared; changed:',changed)
    if changed:raise SystemExit(1)

if __name__=='__main__':main()
