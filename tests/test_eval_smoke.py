"""Smoke test: the eval harness runs on three offers without network and returns its metric keys."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_harness():
    spec = importlib.util.spec_from_file_location("run_eval", ROOT / "eval" / "run_eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_harness_returns_metric_keys_on_three_offers():
    mod = _load_harness()
    fixtures = mod.load_offers(limit=3)
    assert len(fixtures) == 3
    res = mod.evaluate(fixtures, llm_ok=False)
    for key in ("meta", "verdict", "rules", "macro_rule_f1", "fields", "timing_ms", "misclassified", "per_offer"):
        assert key in res
    assert res["meta"]["extractor_mode"] == "fallback"
    assert res["verdict"]["n"] == 3
    assert set(res["rules"]["per_rule"]) == set(mod.RULE_IDS)
    assert res["timing_ms"]["median_ms"] is not None
