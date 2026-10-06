# Field data templates + script test set

- `*_template.csv`: header-only collection templates. Columns:
  - assessments: anonymous `session_id`, `date` (YYYY-MM-DD), broad
    `locality`, `category`, per-question correctness `q1..q6` ∈ {0,1}
    (score is computed by the script — never transcribed).
  - feedback: `rating` ∈ {1..5}; `comments` holds paraphrased/anonymized
    notes only — never names, phones, OTPs, addresses.
  - sessions: headcounts only (`participants`, `before_n`, `after_n`,
    `feedback_n`, `issues_n`).
  - observations: `severity` ∈ {low,medium,high}, `status` ∈
    {open,fixed,wontfix}; no personal data.
- `demo/`: **DEMO DATA — NOT FIELD RESULTS.** Synthetic rows for testing
  `backend/scripts/analyze_field_data.py` only. Never quote these numbers
  as field evidence, never mix them with real collections.
