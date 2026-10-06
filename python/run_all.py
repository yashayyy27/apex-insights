"""Offline-first reproduction entry point; never claims native Power BI execution."""
import argparse
from pathlib import Path
import sys
import ingest,generate_synthetic_ccep,f1_pipeline,transform,validate,analyse,build_powerbi,validate_powerbi,build_docs,build_previews

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh-public',action='store_true',help='Allow fetching missing public cache pages, respecting rate limits; existing cache is unchanged.')
    args=parser.parse_args()
    ingest.main()
    generate_synthetic_ccep.main()
    f1_pipeline.normalize(f1_pipeline.Client(offline=not args.refresh_public))
    transform.main()
    validate.validate_all()
    analyse.main()
    build_powerbi.main()
    validate_powerbi.main()
    build_docs.main()
    build_previews.main()
    print('Reproduction complete. XLSX export and native Power BI runtime are separate acceptance stages.')

if __name__=='__main__':main()
