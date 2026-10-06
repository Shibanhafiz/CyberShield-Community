"""Tests for scripts/analyze_field_data.py — run ONLY against the labeled
demo CSVs in docs/vtu/data/demo/ (DEMO DATA — NOT FIELD RESULTS)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

from analyze_field_data import (  # noqa: E402
    check_assessment,
    check_feedback,
    load_csv,
    summarize,
)

DEMO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "..", "docs", "vtu", "data", "demo")


def _demo(name):
    return os.path.normpath(os.path.join(DEMO, name))


def test_demo_files_are_labeled_not_field_data():
    with open(os.path.join(DEMO, "README.md"), encoding="utf-8") as f:
        assert "NOT FIELD RESULTS" in f.read()


def test_assessment_validation_flags_defects():
    rows, bad = load_csv(_demo("demo_pre.csv"), "pre")
    assert bad == []
    flags = []
    scores = check_assessment(rows, "pre", flags)
    codes = {f["code"] for f in flags}
    assert "duplicate_session_id" in codes
    assert "invalid_answer" in codes
    assert scores == {"demo-s01": 3, "demo-s02": 2, "demo-s03": 2}


def test_summary_uses_matched_pairs_only():
    pre_rows, _ = load_csv(_demo("demo_pre.csv"), "pre")
    post_rows, _ = load_csv(_demo("demo_post.csv"), "post")
    pre = check_assessment(pre_rows, "pre", [])
    post = check_assessment(post_rows, "post", [])
    out = summarize(pre, post, [4, 5],
                    {"sessions": 2, "participants": 20},
                    {"observations": 2, "open": 1})
    assert out["matched_pairs"] == 3
    assert out["unmatched_post_only"] == 1  # demo-s09 flagged by count
    assert out["avg_difference"] == 2.0
    assert out["completion_rate"] == 1.0
    assert out["feedback_avg_rating"] == 4.5
    assert out["small_sample_caveat"] is True


def test_bad_header_and_unreadable_rejected():
    rows, bad = load_csv(_demo("demo_feedback.csv"), "pre")
    assert rows == [] and bad[0]["code"] == "bad_header"
    rows, bad = load_csv(_demo("no-such-file.csv"), "pre")
    assert rows == [] and bad[0]["code"] == "unreadable"


def test_feedback_rating_bounds():
    flags = []
    assert check_feedback([{"session_id": "a", "rating": "6"}], flags) == []
    assert flags and flags[0]["code"] == "invalid_rating"
