# VTU 1BCP308 field-study templates — CyberShield Community

> TEMPLATES ONLY. Fill with real field data. Do NOT fabricate responses,
> counts, findings, interviews, photographs or impact statistics.

## 1. Stakeholder information

| Field | Value |
|---|---|
| Stakeholder type (student / shopkeeper / homemaker / senior citizen / …) | |
| Approximate number of participants | |
| Date | |
| Location (locality only) | |
| Purpose of interaction | |
| Key concerns raised | |

## 2. Baseline survey (before awareness)

| # | Question | Response scale |
|---|---|---|
| 1 | Have you received a suspicious SMS/WhatsApp message in the last 3 months? | Yes / No |
| 2 | Can you name two signs of a phishing message? | Open text |
| 3 | What do you do when a message demands an OTP urgently? | Open text |
| 4 | Have you or someone you know lost money to an online scam? | Yes / No / Prefer not to say |
| 5 | Awareness quiz score (before) | ___ / total |

Findings (to be filled): …

## 3. Community reports log

| Date | Category | Approximate area | Observed indicators | Notes |
|---|---|---|---|---|
| | | | | |

(Cross-check against `/api/community/*` exports; never copy raw report text
containing personal data into this document.)

## 4. Awareness activity record

| Field | Value |
|---|---|
| Topic (OTP fraud / digital arrest / …) | |
| Participants (count only) | |
| Duration | |
| Materials used | |
| Before score (avg %) | |
| After score (avg %) | |
| Participant feedback (anonymized) | |

## 5. Impact measurement

| Metric | Source | Before | After |
|---|---|---|---|
| Total community reports | `/api/community/stats` | | |
| Scam categories identified | `/api/community/categories` | | |
| Awareness quiz avg score | quiz module (later phase) | | |
| Duplicate report rate | `report_count` aggregates | | |

Report only measured values with dates. Leave blank what was not measured.
