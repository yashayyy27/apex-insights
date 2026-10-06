"""Shared paths, deterministic CSV serialization, and source manifests."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config/project.json').read_text())

def save_csv(frame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format='%.6f', lineterminator='\n')

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_tables(domain):
    return {p.stem: pd.read_csv(p) for p in sorted((ROOT / 'data/processed' / domain).glob('*.csv'))}

def write_json(value, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def update_processed_manifest():
    """Refresh hashes after a stage writes CSVs, including analytical extracts."""
    manifest={str(p.relative_to(ROOT)):{'sha256':sha256(p),'bytes':p.stat().st_size}
              for p in sorted((ROOT/'data/processed').rglob('*.csv'))}
    write_json(manifest,ROOT/'outputs/processed_manifest.json')
