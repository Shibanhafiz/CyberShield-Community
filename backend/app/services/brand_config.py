"""Well-known brand list for impersonation/typosquatting heuristics.

DEVELOPMENT list only — a small sample for validating the detection
pipeline, not a production brand-protection feed. Extend via this file
(or a future admin-managed source); the analyzer imports BRANDS from here.
"""

BRANDS = [
    "google",
    "microsoft",
    "amazon",
    "apple",
    "paypal",
    "instagram",
    "facebook",
    "whatsapp",
    "netflix",
]
