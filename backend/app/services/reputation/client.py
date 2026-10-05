"""Reputation-service adapter (Phase 3: interface only, no providers).

Future providers (Google Safe Browsing, VirusTotal, etc.) implement
check_domain_reputation(domain) behind this interface. Until a legitimate
API key is configured, the adapter honestly reports unavailable — the API
surfaces that state instead of fabricating vendor verdicts.
"""


def check_domain_reputation(domain: str) -> dict:
    """Return availability + verdict. Currently always unavailable."""
    return {
        "available": False,
        "source": None,
        "verdict": None,
        "reason": "No reputation provider configured. Static analysis only.",
    }
