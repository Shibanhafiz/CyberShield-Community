"""Summarize anonymized CyberShield field-study CSVs (stdlib only).

Usage:
    cd backend
    python scripts/analyze_field_data.py --pre <csv> --post <csv>
        [--feedback <csv> --sessions <csv> --observations <csv>]
        [--output summary.json]

Reads the templates in docs/vtu/data/*_template.csv. Validates columns
and values, flags bad rows (duplicates, missing answers, impossible
scores, inconsistent sessions) WITHOUT modifying or dropping anything
silently, then prints aggregate statistics. Prints counts and flagged
row numbers only — never participant content.

Exit status: 0 on success (warnings allowed), 1 on unreadable files or
unknown arguments. Test the script against docs/vtu/data/demo/ (labeled
DEMO DATA — NOT FIELD RESULTS), never against fabricated "field" files.
"""

import argparse
import csv
import json
import re
import sys
from datetime import date

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEVERITIES = {"low", "medium", "high"}
STATUSES = {"open", "fixed", "wontfix"}

SCHEMAS = {
    "pre": ["session_id", "date", "locality", "category",
            "q1", "q2", "q3", "q4", "q5", "q6"],
    "post": ["session_id", "date", "locality", "category",
             "q1", "q2", "q3", "q4", "q5", "q6"],
    "feedback": ["session_id", "date", "topic", "rating", "category",
                 "locality", "comments"],
    "sessions": ["session_code", "date", "locality", "category",
                 "participants", "before_n", "after_n", "feedback_n",
                 "issues_n"],
    "observations": ["obs_id", "session_code", "date", "category",
                     "activity", "issue", "severity", "proposal", "status"],
}


def _int_or_none(value):
    try:
        return int(str(value).strip())
    except (ValueError, AttributeError, TypeError):
        return None


def load_csv(path, kind):
    """Return (rows, flags). Flags are {row_no, code, detail} dicts."""
    flags = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != SCHEMAS[kind]:
                return [], [{"row_no": 0, "code": "bad_header",
                             "detail": f"expected {SCHEMAS[kind]}, "
                                       f"got {reader.fieldnames}"}]
            rows = list(reader)
    except (OSError, UnicodeError) as exc:
        return [], [{"row_no": 0, "code": "unreadable", "detail": str(exc)}]
    return rows, flags


def check_assessment(rows, kind, flags):
    """Validate q1..q6 rows; return {session_id: score} for clean rows."""
    scores = {}
    seen = set()
    for n, r in enumerate(rows, start=2):  # 1-based + header row
        sid = (r.get("session_id") or "").strip()
        if not sid:
            flags.append({"row_no": n, "code": "missing_session_id",
                          "detail": kind})
            continue
        if sid in seen:
            flags.append({"row_no": n, "code": "duplicate_session_id",
                          "detail": f"{kind}:{sid}"})
            continue
        seen.add(sid)
        if r.get("date", "").strip() and not DATE_RE.match(r["date"].strip()):
            flags.append({"row_no": n, "code": "bad_date",
                          "detail": f"{kind}:{sid}"})
        values = []
        bad = False
        for q in ("q1", "q2", "q3", "q4", "q5", "q6"):
            v = _int_or_none(r.get(q))
            if v not in (0, 1):
                flags.append({"row_no": n, "code": "invalid_answer",
                              "detail": f"{kind}:{sid}:{q}={r.get(q)!r}"})
                bad = True
                break
            values.append(v)
        if not bad:
            scores[sid] = sum(values)
    return scores


def check_feedback(rows, flags):
    ratings = []
    seen = set()
    for n, r in enumerate(rows, start=2):
        sid = (r.get("session_id") or "").strip()
        if sid:
            if sid in seen:
                flags.append({"row_no": n, "code": "duplicate_session_id",
                              "detail": f"feedback:{sid}"})
            seen.add(sid)
        v = _int_or_none(r.get("rating"))
        if v is None or not 1 <= v <= 5:
            flags.append({"row_no": n, "code": "invalid_rating",
                          "detail": f"feedback row {n}"})
            continue
        ratings.append(v)
    return ratings


def check_sessions(rows, flags):
    total_participants = 0
    for n, r in enumerate(rows, start=2):
        for col in ("participants", "before_n", "after_n", "feedback_n",
                    "issues_n"):
            v = _int_or_none(r.get(col))
            if v is None or v < 0:
                flags.append({"row_no": n, "code": "impossible_value",
                              "detail": f"sessions:{col}={r.get(col)!r}"})
                break
        else:
            total_participants += _int_or_none(r["participants"])
            b, a = _int_or_none(r["before_n"]), _int_or_none(r["after_n"])
            if a > b:
                flags.append({"row_no": n, "code": "inconsistent_counts",
                              "detail": "after_n exceeds before_n"})
    return {"sessions": len(rows), "participants": total_participants}


def check_observations(rows, flags):
    open_count = 0
    for n, r in enumerate(rows, start=2):
        if not (r.get("obs_id") or "").strip():
            flags.append({"row_no": n, "code": "missing_obs_id",
                          "detail": f"row {n}"})
        if (r.get("severity") or "").strip().lower() not in SEVERITIES:
            flags.append({"row_no": n, "code": "invalid_severity",
                          "detail": f"row {n}"})
        status = (r.get("status") or "").strip().lower()
        if status not in STATUSES:
            flags.append({"row_no": n, "code": "invalid_status",
                          "detail": f"row {n}"})
        elif status == "open":
            open_count += 1
    return {"observations": len(rows), "open": open_count}


def summarize(pre_scores, post_scores, ratings, session_info, obs_info):
    matched = sorted(set(pre_scores) & set(post_scores))
    only_pre = sorted(set(pre_scores) - set(post_scores))
    only_post = sorted(set(post_scores) - set(pre_scores))
    diffs = [post_scores[s] - pre_scores[s] for s in matched]
    n = len(matched)
    avg = lambda xs: round(sum(xs) / len(xs), 2) if xs else None
    avg_pre = avg([pre_scores[s] for s in matched])
    avg_post = avg([post_scores[s] for s in matched])
    avg_diff = avg(diffs)
    improvement_pct = (round(avg_diff / avg_pre * 100, 1)
                       if avg_pre else None)
    return {
        "participants_pre": len(pre_scores),
        "participants_post": len(post_scores),
        "matched_pairs": n,
        "unmatched_pre_only": len(only_pre),
        "unmatched_post_only": len(only_post),
        "completion_rate": round(n / len(pre_scores), 3) if pre_scores else None,
        "avg_pre_score": avg_pre,
        "avg_post_score": avg_post,
        "avg_difference": avg_diff,
        "improvement_pct": improvement_pct,
        "small_sample_caveat": n < 30,
        "feedback_responses": len(ratings),
        "feedback_avg_rating": avg(ratings),
        "sessions": session_info,
        "observations": obs_info,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarize anonymized field-study CSVs.")
    parser.add_argument("--pre", help="pre-assessment CSV")
    parser.add_argument("--post", help="post-assessment CSV")
    parser.add_argument("--feedback", help="feedback CSV")
    parser.add_argument("--sessions", help="field sessions CSV")
    parser.add_argument("--observations", help="observations CSV")
    parser.add_argument("--output", help="write JSON summary to file")
    args = parser.parse_args(argv)

    flags = []
    pre_scores, post_scores, ratings = {}, {}, {}
    session_info, obs_info = {"sessions": 0, "participants": 0}, \
        {"observations": 0, "open": 0}
    if args.pre:
        rows, bad = load_csv(args.pre, "pre")
        flags += bad
        if not bad:
            pre_scores = check_assessment(rows, "pre", flags)
    if args.post:
        rows, bad = load_csv(args.post, "post")
        flags += bad
        if not bad:
            post_scores = check_assessment(rows, "post", flags)
    if args.feedback:
        rows, bad = load_csv(args.feedback, "feedback")
        flags += bad
        if not bad:
            ratings = check_feedback(rows, flags)
    if args.sessions:
        rows, bad = load_csv(args.sessions, "sessions")
        flags += bad
        if not bad:
            session_info = check_sessions(rows, flags)
    if args.observations:
        rows, bad = load_csv(args.observations, "observations")
        flags += bad
        if not bad:
            obs_info = check_observations(rows, flags)

    summary = summarize(pre_scores, post_scores, ratings, session_info,
                        obs_info)
    out = {"summary": summary, "flags": flags,
           "generated_on": date.today().isoformat()}
    text = json.dumps(out, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
