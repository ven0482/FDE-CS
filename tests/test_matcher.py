"""Small tests for the matching logic. Run with: pytest -q"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from matcher import find_similar_tickets


def load_data():
    with (ROOT / "data" / "tickets.json").open(encoding="utf-8") as file:
        history = json.load(file)["tickets"]
    with (ROOT / "data" / "new_tickets_example.json").open(encoding="utf-8") as file:
        examples = json.load(file)["new_tickets"]
    return history, examples


def test_password_reset_finds_related_ticket():
    history, examples = load_data()
    result = find_similar_tickets(examples[0], history, threshold=0.08)
    assert result["match_found"] is True
    assert result["matches"][0]["ticket_id"] == "T-1001"


def test_revenue_chart_finds_related_ticket():
    history, examples = load_data()
    result = find_similar_tickets(examples[1], history, threshold=0.08)
    assert result["match_found"] is True
    assert result["matches"][0]["ticket_id"] == "T-1003"


def test_duplicate_charge_finds_related_ticket():
    history, examples = load_data()
    result = find_similar_tickets(examples[2], history, threshold=0.08)
    assert result["match_found"] is True
    assert result["matches"][0]["ticket_id"] in {"T-1005", "T-1006"}


def test_snowflake_case_can_abstain():
    history, examples = load_data()
    result = find_similar_tickets(examples[3], history, threshold=0.12)
    assert result["match_found"] is False
    assert result["matches"] == []


def test_results_are_sorted_highest_score_first():
    history, examples = load_data()
    result = find_similar_tickets(examples[0], history, threshold=0.0)
    scores = [item["similarity_score"] for item in result["matches"]]
    assert scores == sorted(scores, reverse=True)


def test_same_ticket_id_is_not_returned_as_a_match():
    history, _ = load_data()
    same_ticket = dict(history[0])
    result = find_similar_tickets(same_ticket, history, threshold=0.0)
    assert all(item["ticket_id"] != same_ticket["ticket_id"] for item in result["matches"])
