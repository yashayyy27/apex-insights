"""Adversarial contract tests plus full dataset integration validation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
import pandas as pd
import numpy as np
import pytest
from validate import inspect_frame,validate_all
from f1_pipeline import seconds,completed_status

def failed(frame):
    return {x['check'].split('.')[-1] for x in inspect_frame('fmcg','FactSales',frame) if not x['passed']}

def fixture():
    return pd.DataFrame([dict(Date='2024-01-01',ProductKey=1,CustomerKey=1,DataClass='SYNTHETIC',Units=10,NetPrice=2.5,UnitCost=1.2,Revenue=25.,COGS=12.,GrossProfit=13.,VolumeLitres=5.,DiscountDepth=0.)])

def test_known_valid_sales():
    assert not failed(fixture())

def test_duplicate_rejected():
    frame=fixture()
    assert 'primary_key' in failed(pd.concat([frame,frame]))

def test_fake_public_label_rejected():
    frame=fixture();frame.loc[0,'DataClass']='PUBLIC'
    assert 'provenance' in failed(frame)

def test_revenue_corruption_rejected():
    frame=fixture();frame.loc[0,'Revenue']=26
    assert {'revenue_identity','gross_profit_identity'}.issubset(failed(frame))

def test_missing_cost_and_invalid_date_rejected():
    frame=fixture();frame.loc[0,'UnitCost']=np.nan;frame.loc[0,'Date']='2024-02-30'
    assert {'required_not_null','valid_dates'}.issubset(failed(frame))

def test_duration_units():
    assert seconds('1:32.123')==pytest.approx(92.123)
    assert seconds('1:02:03.5')==pytest.approx(3723.5)
    assert seconds('') is None

@pytest.mark.parametrize('status,completed',[('Finished',True),('Lapped',True),('+1 Lap',True),('+2 Laps',True),('Retired',False),('Disqualified',False)])
def test_public_completion_status_variants(status,completed):
    assert completed_status(status)==completed

def test_lapped_finish_flag_corruption_rejected():
    frame=pd.DataFrame([dict(RaceKey=202408,DriverKey='tsunoda',ConstructorKey='rb',DataClass='PUBLIC_DERIVED',
        Grid=8,FinishPosition=8,Points=4.,Laps=77,Status='Lapped',ClassifiedFinish=0,PositionGain=np.nan)])
    assert any(x['check'].endswith('completion_status_mapping') and not x['passed'] for x in inspect_frame('f1','FactRaceResults',frame))

def test_distribution_range_rejected():
    frame=pd.DataFrame([dict(Date='2024-01-01',ProductKey=1,CustomerKey=1,DataClass='SYNTHETIC',ActiveStoreDays=11,EligibleStoreDays=10)])
    assert any(x['check'].endswith('distribution_bounds') and not x['passed'] for x in inspect_frame('fmcg','FactDistribution',frame))

def test_full_dataset_validation():
    assert validate_all()['status']=='PASS'
