from src.eval.metrics import condition_f1

def test_condition_metric():
    pred = [{"name": "hypertension"}]
    gold = [{"name": "hypertension"}, {"name": "asthma"}]
    m = condition_f1(pred, gold)
    assert 0.0 <= m["f1"] <= 1.0