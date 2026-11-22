"""
Tests for System C v3 recovery logic, using a scripted fake LLM.
Uses the Online Retail database; skipped if it is not present locally.
"""
import sys
from pathlib import Path

import pytest

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "src"))

import nl_to_sql
import agents.analysis_agent as analysis_module
import agents.orchestrator_c_v3 as v3
from database import online_retail_database_path
from nl_to_sql import ONLINE_RETAIL_SCHEMA_WITH_DEFINITIONS as SCHEMA

pytestmark = pytest.mark.skipif(not Path(online_retail_database_path).exists(),
                                reason="Online Retail database not available")

N = "InvoiceNo NOT LIKE 'C%' AND Quantity > 0 AND UnitPrice > 0"
QUESTION = "How many countries have a gross revenue greater than 100,000?"
WRONG = (f"SELECT COUNT(DISTINCT Country) FROM online_retail WHERE {N} "
         f"GROUP BY Country HAVING SUM(Quantity * UnitPrice) > 100000")
RIGHT = (f"SELECT COUNT(*) FROM (SELECT Country FROM online_retail WHERE {N} "
         f"GROUP BY Country HAVING SUM(Quantity * UnitPrice) > 100000)")


class FakeLLM:
    def __init__(self, repairs):
        self.repairs = list(repairs)
        self.repair_calls = 0

    def __call__(self, prompt, temperature=None, seed=None, model=None):
        if prompt.rstrip().endswith("CORRECTED SQL QUERY:"):
            self.repair_calls += 1
            return self.repairs.pop(0) if self.repairs else WRONG
        if prompt.rstrip().endswith("SQL QUERY:"):
            return WRONG
        if "INVALID" in prompt:
            return "VALID"
        return "answer"


def install(fake, monkeypatch):
    for module in (nl_to_sql, analysis_module, v3):
        monkeypatch.setattr(module, "generate_response", fake)


def test_group_by_error_is_detected_and_repaired(monkeypatch):
    fake = FakeLLM([RIGHT])
    install(fake, monkeypatch)
    result = v3.orchestrate_c_v3(QUESTION, online_retail_database_path, SCHEMA)
    assert result["success"]
    assert result["rows"] == [(6,)]
    assert result["recovery_attempts"] == 1


def test_identical_repair_is_retried_not_abandoned(monkeypatch):
    fake = FakeLLM([WRONG, RIGHT])
    install(fake, monkeypatch)
    result = v3.orchestrate_c_v3(QUESTION, online_retail_database_path, SCHEMA)
    assert result["success"]
    assert result["rows"] == [(6,)]
    assert result["recovery_attempts"] == 2


def test_abstains_when_repairs_never_fix_the_problem(monkeypatch):
    fake = FakeLLM([])
    install(fake, monkeypatch)
    result = v3.orchestrate_c_v3(QUESTION, online_retail_database_path, SCHEMA)
    assert not result["success"]
    assert fake.repair_calls == v3.MAX_REPAIRS


def test_single_value_check_ignores_multi_row_questions():
    execution = {"success": True, "rows": [("UK", 1.0), ("NL", 2.0)]}
    assert v3.deterministic_check("Which 5 countries have the highest revenue?", execution) is None
    assert v3.deterministic_check("How many customers are there?", execution) is not None
