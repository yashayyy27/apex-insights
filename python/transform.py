"""Standardise types, reject dirty keys, and build a constrained SQL mart."""
import shutil
import sqlite3
import pandas as pd
from common import ROOT, read_tables, save_csv, update_processed_manifest

def stage_synthetic():
    output = ROOT / 'data/processed/fmcg'
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / 'data/synthetic/fmcg').glob('*.csv')):
        df = pd.read_csv(path)
        for col in df.select_dtypes('object').columns:
            df[col] = df[col].str.strip()
        if not df.DataClass.eq('SYNTHETIC').all():
            raise ValueError('Mixed provenance: ' + path.name)
        # Exact rows may not be silently discarded: key checks own dedup decisions.
        if df.duplicated().any():
            raise ValueError('Duplicate input rows: ' + path.name)
        save_csv(df, output / path.name)

def build_sql():
    from contracts import CONTRACTS, relationships
    db = ROOT / 'data/processed/apex.sqlite'
    db.unlink(missing_ok=True)
    connection = sqlite3.connect(db)
    connection.execute('PRAGMA foreign_keys=ON')
    frames = {}
    ddls = ['-- SQLite 3 analytical mart; generated from contracts.py and executed by transform.py.\nPRAGMA foreign_keys=ON;']
    all_rel = []
    for domain in ['fmcg', 'f1', 'public']:
        for name, frame in read_tables(domain).items():
            frames[(domain, name)] = frame
        all_rel += [(domain, *x) for x in relationships(domain)]
    # Load dimensions before facts and circuit before race.
    order = sorted(frames, key=lambda x: (0 if x[1] not in ['DimRace'] and x[1].startswith('Dim') else 1 if x[1] == 'DimRace' else 2, x))
    for domain, name in order:
        frame = frames[(domain, name)]
        contract = CONTRACTS.get((domain, name), {'key': ['Metric'], 'nullable': []})
        cols = []
        for col in frame:
            dtype = 'INTEGER' if pd.api.types.is_integer_dtype(frame[col]) else 'REAL' if pd.api.types.is_numeric_dtype(frame[col]) else 'TEXT'
            nullable = col in contract.get('nullable', [])
            cols.append(f'"{col}" {dtype}' + ('' if nullable else ' NOT NULL'))
        cols.append('PRIMARY KEY (' + ', '.join('"' + x + '"' for x in contract['key']) + ')')
        for dom, fact, fk, dim, dk in all_rel:
            if dom == domain and fact == name:
                cols.append(f'FOREIGN KEY ("{fk}") REFERENCES "{domain}_{dim}"("{dk}")')
        allowed = "'SYNTHETIC'" if domain == 'fmcg' else "'PUBLIC','PUBLIC_DERIVED'"
        cols.append(f'CHECK (DataClass IN ({allowed}))')
        for col in ['Revenue', 'COGS', 'Units', 'TargetRevenue', 'MarketRevenue', 'Points', 'Trials', 'RepeatWithin28d']:
            if col in frame:
                cols.append(f'CHECK ("{col}" >= 0)')
        ddl = f'CREATE TABLE "{domain}_{name}" (\n  ' + ',\n  '.join(cols) + '\n);'
        connection.execute(ddl)
        ddls.append(ddl)
        values = [tuple(None if pd.isna(v) else v.item() if hasattr(v, 'item') else v for v in row) for row in frame.itertuples(index=False, name=None)]
        connection.executemany(f'INSERT INTO "{domain}_{name}" VALUES (' + ','.join('?' for _ in frame) + ')', values)
    connection.commit()
    for domain, name in frames:
        if name.startswith('Fact'):
            for col in ['Date', 'RaceKey', 'ProductKey', 'DriverKey']:
                if col in frames[(domain, name)]:
                    connection.execute(f'CREATE INDEX "ix_{domain}_{name}_{col}" ON "{domain}_{name}"("{col}")')
    (ROOT / 'sql/schema.sql').write_text('\n\n'.join(ddls) + '\n')
    connection.executescript((ROOT / 'sql/transformations.sql').read_text())
    connection.close()
    update_processed_manifest()
    print('Constrained SQL mart built:', len(frames), 'tables')

def main():
    stage_synthetic()
    build_sql()

if __name__ == '__main__':
    main()
