"""Curate small, attributed public facts. Does not scrape protected reports."""
from common import ROOT, save_csv, write_json, sha256
import pandas as pd

def main():
    url = 'https://www.cocacolaep.com/news-and-stories/q4-and-fy-financial-results/'
    rows = [
        ['Revenue growth', 0.035, 'Adjusted comparable FXN'],
        ['Operating profit growth', 0.080, 'Adjusted comparable FXN'],
        ['EPS growth', 0.065, 'Comparable FXN'],
    ]
    df = pd.DataFrame(rows, columns=['Metric', 'Value', 'Basis'])
    df['Scope'] = 'CCEP Group FY2024 vs FY2023'
    df['SourceURL'] = url
    df['PublishedDate'] = '2025-02-14'
    df['DataClass'] = 'PUBLIC'
    path = ROOT / 'data/raw/public_ccep_context.csv'
    save_csv(df, path)
    save_csv(df, ROOT / 'data/processed/public/PublicContext.csv')
    write_json({'source_url': url, 'access': 'Manually curated public factual extract; direct fetch 403',
                'verified_date': '2026-10-06', 'sha256': sha256(path),
                'scope': 'Group growth, not Australia sales; no synthetic calibration'},
               ROOT / 'data/raw/ccep_context_manifest.json')

if __name__ == '__main__':
    main()
