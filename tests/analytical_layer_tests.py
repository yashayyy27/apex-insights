"""Independent reconciliation and SQL execution checks, beyond row contracts."""
from pathlib import Path
import sqlite3
import json
import re
import pytest

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def connection():
    db=sqlite3.connect(ROOT/'data/processed/apex.sqlite')
    yield db
    db.close()

def test_all_analysis_queries_execute(connection):
    text=re.sub(r'--[^\n]*','',(ROOT/'sql/analysis_queries.sql').read_text())
    statements=[s.strip() for s in text.split(';') if s.strip()]
    for statement in statements:
        assert connection.execute(statement).description is not None

def test_no_fact_fanout(connection):
    base=connection.execute('SELECT COUNT(*),SUM(Revenue) FROM fmcg_FactSales').fetchone()
    view=connection.execute('SELECT COUNT(*),SUM(Revenue) FROM commercial_sales').fetchone()
    assert base[0]==view[0]
    assert base[1]==pytest.approx(view[1],abs=.01)

def test_exact_bridge_vs_independent_period_totals(connection):
    totals=connection.execute('SELECT Year,SUM(Revenue) FROM commercial_sales GROUP BY Year ORDER BY Year').fetchall()
    components=connection.execute('SELECT SUM(VolumeEffect+PriceMixEffect+InteractionEffect+NewProductEffect) FROM revenue_bridge').fetchone()[0]
    assert components==pytest.approx(totals[1][1]-totals[0][1],abs=.01)

def test_campaign_units_and_profit_match_sales_population(connection):
    direct=connection.execute("SELECT SUM(Units),SUM(GrossProfit-TradeSpend) FROM fmcg_FactSales WHERE PromotionFlag=1").fetchone()
    promo=connection.execute('SELECT SUM(ActualUnits),SUM(ActualGP-TradeSpend) FROM fmcg_FactPromotion').fetchone()
    assert direct[0]==promo[0]
    assert direct[1]==pytest.approx(promo[1],abs=.01)

def test_repeat_weighted_cohort_controls(connection):
    for repeat,trial,ratio in connection.execute('SELECT Repeats,Trials,CohortRepeatRate FROM innovation_review'):
        assert 0<=repeat<=trial
        assert ratio==pytest.approx(repeat/trial)

def test_teammate_comparisons_not_multiplied(connection):
    max_count=connection.execute('SELECT MAX(ComparableStarts) FROM teammate_comparison WHERE Season=2024').fetchone()[0]
    races=connection.execute('SELECT COUNT(*) FROM f1_DimRace WHERE Season=2024').fetchone()[0]
    assert 0<max_count<=races

def test_pit_null_preserved(connection):
    row=connection.execute("SELECT DurationSeconds,TimingEligible FROM f1_FactPitStops WHERE RaceKey=202412 AND DriverKey='tsunoda' AND Stop=1").fetchone()
    assert row==(None,0)

def test_model_dax_field_references_exist():
    for label in ['Commercial','Motorsport']:
        model=json.loads((ROOT/f'powerbi/{label}.SemanticModel/model.bim').read_text())['model']
        tablemap={t['name']:{c['name'] for c in t['columns']} for t in model['tables']}
        measures={m['name'] for t in model['tables'] for m in t.get('measures',[])}
        for table in model['tables']:
            for measure in table.get('measures',[]):
                expression=measure['expression']
                for tbl,column in re.findall(r'([A-Za-z][A-Za-z0-9_]*)\[([^\]]+)\]',expression):
                    assert tbl in tablemap,(label,measure['name'],tbl)
                    assert column in tablemap[tbl],(label,measure['name'],tbl,column)
                unqualified=re.sub(r'[A-Za-z][A-Za-z0-9_]*\[[^\]]+\]','',expression)
                for name in re.findall(r'\[([^\]]+)\]',unqualified):
                    assert name in measures,(label,measure['name'],name)

def test_parameter_metadata_and_model_contract():
    for label in ['Commercial','Motorsport']:
        model=json.loads((ROOT/f'powerbi/{label}.SemanticModel/model.bim').read_text())['model']
        date=next(t for t in model['tables'] if t['name']=='DimDate')
        assert date['dataCategory']=='Time'
        assert next(c for c in date['columns'] if c['name']=='Date')['isKey']
        for t in model['tables']:
            for c in t['columns']:
                assert 'groupByColumns' not in c
                if 'relatedColumnDetails' in c:
                    assert c['relatedColumnDetails']['groupByColumns'][0]['groupingColumn'] in {x['name'] for x in t['columns']}
        assert all(r['toCardinality']=='one' and r['crossFilteringBehavior']=='oneDirection' for r in model['relationships'])
