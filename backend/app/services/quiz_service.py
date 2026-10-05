"""Quiz, awareness and impact logic. All scoring happens here, server-side.

Recommendations are a deterministic category->topic mapping (no LLM).
Impact metrics aggregate real rows only; empty states are explicit.
"""

import json
import logging
import random
import uuid

from sqlalchemy.orm import Session

from ..models.awareness_session import AwarenessSession
from ..models.learning_topic import LearningTopic
from ..models.quiz_attempt import QuizAttempt
from ..models.quiz_question import QuizQuestion

logger = logging.getLogger("cybershield.quiz_service")

# Quiz category -> (topic slug, topic title) for review recommendations.
CATEGORY_TOPICS: dict[str, tuple[str, str]] = {
    "Phishing": ("phishing", "Phishing Messages & Fake Links"),
    "OTP & Banking": ("otp-banking-scams", "OTP & Banking Scams"),
    "Job Scams": ("job-scams", "Job & Work-From-Home Scams"),
    "Investment Scams": ("investment-scams", "Investment & Trading Scams"),
    "Delivery Scams": ("delivery-scams", "Delivery & Courier Scams"),
    "Digital Arrest": ("digital-arrest", "Digital-Arrest & Police-Threat Scams"),
    "Fake Support": ("fake-support", "Fake Customer-Support Scams"),
    "Malicious Apps": ("malicious-apps", "Malicious Apps & APKs"),
}

ASSESSMENT_SIZE = 6


def validate_session_id(session_id: str) -> str:
    try:
        return str(uuid.UUID(session_id))
    except (ValueError, AttributeError, TypeError):
        raise ValueError("session_id must be a valid UUID.")


def scenario_choices(scenario) -> list[str]:
    """Deterministic per-scenario shuffle: mixed order, stable, stateless."""
    options = json.loads(scenario.incorrect_actions) + [scenario.correct_action]
    rng = random.Random(scenario.scenario_id)
    rng.shuffle(options)
    return options


def check_scenario_answer(scenario, selected: int) -> dict:
    options = scenario_choices(scenario)
    if not 0 <= selected < len(options):
        raise ValueError("Invalid choice index.")
    safe = options[selected] == scenario.correct_action
    return {
        "safe_choice": safe,
        "correct_action": scenario.correct_action,
        "warning_signals": json.loads(scenario.warning_signals),
        "explanation": scenario.explanation,
    }


def parse_question(q: QuizQuestion) -> dict:
    return {
        "id": q.id,
        "category": q.category,
        "question": q.question,
        "options": json.loads(q.options),
        "difficulty": q.difficulty,
    }


def get_questions(db: Session, quiz_type: str, count: int) -> list[dict]:
    """Randomized question set WITHOUT correct answers."""
    if quiz_type == "assessment":
        pool = db.query(QuizQuestion).filter(
            QuizQuestion.is_assessment.is_(True),
            QuizQuestion.is_demo_data.is_(False),
        ).all()
        count = min(count, ASSESSMENT_SIZE, len(pool)) or len(pool)
    else:
        pool = db.query(QuizQuestion).filter(
            QuizQuestion.is_assessment.is_(False),
            QuizQuestion.is_demo_data.is_(False),
        ).all()
        count = min(max(count, 1), 50, len(pool))
    return [parse_question(q) for q in random.sample(pool, count)] if pool else []


def build_recommendations(category_scores: dict) -> list[dict]:
    """Deterministic: every imperfect category maps to its topic, worst first."""
    recs = []
    for cat, tally in category_scores.items():
        total = tally["total"] or 1
        accuracy = tally["correct"] / total
        if accuracy < 1.0 and cat in CATEGORY_TOPICS:
            slug, title = CATEGORY_TOPICS[cat]
            recs.append({"slug": slug, "title": title, "accuracy": round(accuracy, 2)})
    return sorted(recs, key=lambda r: r["accuracy"])


def score_answers(
    db: Session, session_id: str, quiz_type: str, answers: list[dict],
    assessment_only: bool = False,
) -> dict:
    """Score submitted answers against the DB bank. Raises ValueError."""
    session_id = validate_session_id(session_id)
    if not answers:
        raise ValueError("At least one answer is required.")

    qids = [a["question_id"] for a in answers]
    if len(set(qids)) != len(qids):
        raise ValueError("Duplicate answers for the same question.")
    questions = db.query(QuizQuestion).filter(QuizQuestion.id.in_(qids)).all()
    if len(questions) != len(qids):
        raise ValueError("One or more question IDs are invalid.")
    if assessment_only and any(not q.is_assessment for q in questions):
        raise ValueError("This assessment accepts only assessment questions.")

    by_id = {q.id: q for q in questions}
    score, category_scores, results = 0, {}, []
    for a in answers:
        q = by_id[a["question_id"]]
        options = json.loads(q.options)
        if not 0 <= a["selected"] < len(options):
            raise ValueError(f"Invalid option index for question {q.id}.")
        correct = a["selected"] == q.correct_option
        score += correct
        tally = category_scores.setdefault(q.category, {"correct": 0, "total": 0})
        tally["total"] += 1
        tally["correct"] += correct
        results.append({
            "question_id": q.id, "question": q.question,
            "category": q.category, "selected": a["selected"],
            "correct_option": q.correct_option, "correct": correct,
            "explanation": q.explanation,
        })

    attempt = QuizAttempt(
        session_id=session_id, quiz_type=quiz_type, score=score,
        total_questions=len(answers),
        category_scores=json.dumps(category_scores),
        results=json.dumps(results, ensure_ascii=False),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    public_results = [
        {"question_id": r["question_id"], "category": r["category"],
         "correct": r["correct"], "explanation": r["explanation"]}
        for r in results
    ]
    return {
        "attempt_id": attempt.id, "score": score, "total": len(answers),
        "category_scores": category_scores,
        "recommendations": build_recommendations(category_scores),
        "results": public_results,
    }


def record_awareness(
    db: Session, session_id: str, kind: str, score: int, total: int
) -> dict:
    """Upsert the session's before/after score; recompute difference."""
    session_id = validate_session_id(session_id)
    row = db.query(AwarenessSession).filter_by(session_id=session_id).first()
    if row is None:
        row = AwarenessSession(session_id=session_id)
        db.add(row)
    if kind == "before":
        row.before_score, row.before_total = score, total
    else:
        row.after_score, row.after_total = score, total
    if row.before_score is not None and row.after_score is not None:
        row.score_difference = row.after_score - row.before_score
    db.commit()
    db.refresh(row)
    return {
        "session_id": row.session_id, "before_score": row.before_score,
        "before_total": row.before_total, "after_score": row.after_score,
        "after_total": row.after_total, "score_difference": row.score_difference,
    }


def get_impact(db: Session) -> dict:
    """Aggregate impact metrics from real rows; explicit empty state."""
    attempts = db.query(QuizAttempt).filter(QuizAttempt.is_demo_data.is_(False)).all()
    sessions = db.query(AwarenessSession).filter(
        AwarenessSession.is_demo_data.is_(False)).all()

    quizzes = [a for a in attempts if a.quiz_type == "quiz"]
    completed = [s for s in sessions
                 if s.before_score is not None and s.after_score is not None]

    def avg(values: list) -> float | None:
        return round(sum(values) / len(values), 2) if values else None

    # Most difficult quiz category (lowest accuracy, min 3 attempts' worth).
    cat_correct: dict[str, int] = {}
    cat_total: dict[str, int] = {}
    for a in quizzes:
        for cat, tally in json.loads(a.category_scores).items():
            cat_correct[cat] = cat_correct.get(cat, 0) + tally["correct"]
            cat_total[cat] = cat_total.get(cat, 0) + tally["total"]
    difficult = None
    worst = 2.0
    for cat, total in cat_total.items():
        if total >= 3:
            acc = cat_correct[cat] / total
            if acc < worst and acc < 1.0:  # perfect categories are never "difficult"
                worst, difficult = acc, cat

    top = db.query(LearningTopic).order_by(LearningTopic.view_count.desc()).first()
    most_reviewed = top.title if top and top.view_count > 0 else None

    has_data = bool(quizzes or completed)
    return {
        "has_data": has_data,
        "quizzes_completed": len(quizzes),
        "awareness_sessions_completed": len(completed),
        "avg_before_score": avg([s.before_score for s in completed]),
        "avg_after_score": avg([s.after_score for s in completed]),
        "avg_score_change": avg([s.score_difference for s in completed
                                 if s.score_difference is not None]),
        "most_difficult_category": difficult,
        "most_reviewed_topic": most_reviewed,
    }
