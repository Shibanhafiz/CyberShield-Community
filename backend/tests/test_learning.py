"""Phase 5 tests: learning content, scenarios, quiz scoring, awareness, impact."""

import uuid


def sid():
    return str(uuid.uuid4())


def test_topics_list_and_detail(isolated_client):
    topics = isolated_client.get("/api/learning/topics").json()
    assert len(topics) == 10
    assert {t["slug"] for t in topics} >= {"phishing", "otp-banking-scams", "digital-arrest"}
    detail = isolated_client.get("/api/learning/topics/phishing").json()
    assert detail["warning_signs"] and detail["should_do"] and detail["never_do"]
    assert detail["example"] and detail["attacker_goal"]
    assert isolated_client.get("/api/learning/topics/nope").status_code == 404


def test_scenarios_list_and_interaction(isolated_client):
    scenarios = isolated_client.get("/api/learning/scenarios").json()
    assert len(scenarios) >= 20
    first = scenarios[0]["scenario_id"]
    detail = isolated_client.get(f"/api/learning/scenarios/{first}").json()
    assert len(detail["choices"]) == 4
    # The correct answer must not be exposed before responding (Phase 5:
    # the detail endpoint used to leak it as `recommended_action`).
    assert "recommended_action" not in detail
    assert "correct_action" not in detail
    # Correct text must not be labeled; find it via message-independent check:
    # answer each position, exactly one must be safe.
    safe_count = 0
    for i in range(4):
        r = isolated_client.post(
            f"/api/learning/scenarios/{first}/answer", json={"selected": i}).json()
        safe_count += r["safe_choice"]
        assert r["correct_action"] and r["explanation"] and r["warning_signals"]
    assert safe_count == 1
    assert isolated_client.get("/api/learning/scenarios/nope").status_code == 404
    bad = isolated_client.post(
        f"/api/learning/scenarios/{first}/answer", json={"selected": 99})
    assert bad.status_code in (400, 422)


def test_quiz_retrieval_no_leak_and_randomized(isolated_client):
    q1 = isolated_client.get("/api/quiz/questions?count=20").json()
    q2 = isolated_client.get("/api/quiz/questions?count=20").json()
    assert len(q1) == 20
    for q in q1:
        assert set(q) == {"id", "category", "question", "options", "difficulty"}
        assert len(q["options"]) == 4
    # Randomized order (overwhelmingly likely to differ across two draws).
    assert [q["id"] for q in q1] != [q["id"] for q in q2]
    assert isolated_client.get("/api/quiz/questions?quiz_type=bogus").status_code == 400


def test_quiz_scoring_all_correct(isolated_client):
    questions = isolated_client.get("/api/quiz/questions?count=5").json()
    # Find correct answers by submitting single-question probes.
    correct = {}
    for q in questions:
        for opt in range(4):
            r = isolated_client.post("/api/quiz/attempt", json={
                "session_id": sid(), "quiz_type": "quiz",
                "answers": [{"question_id": q["id"], "selected": opt}],
            }).json()
            if r["score"] == 1:
                correct[q["id"]] = opt
                break
        assert q["id"] in correct
    full = isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz",
        "answers": [{"question_id": q["id"], "selected": correct[q["id"]]}
                    for q in questions],
    }).json()
    assert full["score"] == 5 and full["total"] == 5
    assert full["recommendations"] == []
    assert all(r["correct"] for r in full["results"])


def test_quiz_scoring_all_wrong_gives_recommendations(isolated_client):
    questions = isolated_client.get("/api/quiz/questions?count=4").json()
    # Pick a wrong option per question by probing (isolated DB, harmless).
    answers = []
    for q in questions:
        for opt in range(4):
            r = isolated_client.post("/api/quiz/attempt", json={
                "session_id": sid(), "quiz_type": "quiz",
                "answers": [{"question_id": q["id"], "selected": opt}],
            }).json()
            if r["score"] == 0:
                answers.append({"question_id": q["id"], "selected": opt})
                break
    full = isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz", "answers": answers,
    }).json()
    assert full["score"] == 0
    assert len(full["recommendations"]) > 0
    assert all("slug" in r and "title" in r for r in full["recommendations"])


def test_quiz_invalid_submissions(isolated_client):
    questions = isolated_client.get("/api/quiz/questions?count=2").json()
    qid = questions[0]["id"]
    assert isolated_client.post("/api/quiz/attempt", json={
        "session_id": "not-a-uuid", "quiz_type": "quiz",
        "answers": [{"question_id": qid, "selected": 0}]}).status_code in (400, 422)
    assert isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz",
        "answers": [{"question_id": 999999, "selected": 0}]}).status_code in (400, 422)
    assert isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz",
        "answers": [{"question_id": qid, "selected": 0},
                    {"question_id": qid, "selected": 1}]}).status_code in (400, 422)
    assert isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz", "answers": []}).status_code in (400, 422)


def test_awareness_before_after_flow(isolated_client):
    s = sid()
    assessment = isolated_client.get("/api/quiz/questions?quiz_type=assessment").json()
    assert len(assessment) == 6
    ids = [q["id"] for q in assessment]

    before = isolated_client.post("/api/awareness/before", json={
        "session_id": s,
        "answers": [{"question_id": i, "selected": 0} for i in ids]}).json()
    assert before["session"]["before_score"] is not None
    assert before["session"]["score_difference"] is None

    # After must use assessment questions only.
    normal = isolated_client.get("/api/quiz/questions?count=1").json()
    bad = isolated_client.post("/api/awareness/after", json={
        "session_id": s,
        "answers": [{"question_id": normal[0]["id"], "selected": 0}]})
    assert bad.status_code == 400

    after = isolated_client.post("/api/awareness/after", json={
        "session_id": s,
        "answers": [{"question_id": i, "selected": 0} for i in ids]}).json()
    assert after["session"]["score_difference"] is not None

    fetched = isolated_client.get(f"/api/awareness/session/{s}").json()
    assert fetched["before_total"] == 6 and fetched["after_total"] == 6
    assert isolated_client.get(f"/api/awareness/session/{sid()}").status_code == 404
    assert isolated_client.get("/api/awareness/session/not-a-uuid").status_code == 400


def test_anonymous_session_no_pii(isolated_client):
    questions = isolated_client.get("/api/quiz/questions?count=1").json()
    r = isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz",
        "answers": [{"question_id": questions[0]["id"], "selected": 0}]}).json()
    blob = str(r).lower()
    for field in ("name", "phone", "email", "otp", "address", "password"):
        assert f'"{field}"' not in blob


def test_impact_empty_and_with_data(isolated_client):
    empty = isolated_client.get("/api/impact/summary").json()
    assert empty["has_data"] is False
    assert empty["quizzes_completed"] == 0
    assert empty["avg_score_change"] is None

    questions = isolated_client.get("/api/quiz/questions?count=2").json()
    isolated_client.post("/api/quiz/attempt", json={
        "session_id": sid(), "quiz_type": "quiz",
        "answers": [{"question_id": q["id"], "selected": 0} for q in questions]})
    filled = isolated_client.get("/api/impact/summary").json()
    assert filled["has_data"] is True
    assert filled["quizzes_completed"] == 1
