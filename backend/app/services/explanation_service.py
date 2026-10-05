"""Explainability: category-aware explanations + safe recommendations.

Wording rules enforced here:
- "potentially suspicious", "several indicators were detected"
- never "definitely a scam" / "100% safe" / "100% scam"
- every response carries the automated-assessment disclaimer.
No model internals (weights, vectors) are exposed.
"""

CATEGORY_LABELS = {
    "NORMAL": "No known scam pattern",
    "PHISHING": "Phishing",
    "BANKING_SCAM": "Banking scam",
    "JOB_SCAM": "Job scam",
    "INVESTMENT_SCAM": "Investment scam",
    "DELIVERY_SCAM": "Delivery scam",
    "OTP_SCAM": "OTP scam",
    "DIGITAL_ARREST": "Digital-arrest scam",
    "FAKE_SUPPORT": "Fake customer support",
    "OTHER_SCAM": "Other suspected scam",
}

CATEGORY_NOTES = {
    "NORMAL": "no scam-specific patterns were recognized",
    "PHISHING": "phishing attempts often combine fake links with credential requests and urgency",
    "BANKING_SCAM": "banking fraud often uses account-suspension scares plus OTP or PIN requests",
    "JOB_SCAM": "job fraud typically promises easy income but demands an advance fee",
    "INVESTMENT_SCAM": "investment fraud typically guarantees unrealistic returns with no risk",
    "DELIVERY_SCAM": "delivery fraud typically invents a stuck parcel and demands a small release fee",
    "OTP_SCAM": "OTP fraud centers on tricking the recipient into revealing a one-time password",
    "DIGITAL_ARREST": "digital-arrest fraud uses fake police or legal threats plus video-call pressure",
    "FAKE_SUPPORT": "fake-support fraud impersonates a company and seeks remote access or payments",
    "OTHER_SCAM": "the pattern resembles prize, rental or advance-fee style fraud",
}

CATEGORY_ACTIONS = {
    "NORMAL": "No action needed, but stay cautious if the sender is unknown.",
    "PHISHING": "Do not open the link or enter credentials. Open the organization's official website or app yourself to check.",
    "BANKING_SCAM": "Do not share OTPs, PINs or card details. Call your bank on its official helpline if worried.",
    "JOB_SCAM": "Do not pay any registration or joining fee. Verify the employer through its official careers page.",
    "INVESTMENT_SCAM": "Do not transfer money. Guaranteed high returns with no risk are a hallmark of fraud — check SEBI-registered advisers only.",
    "DELIVERY_SCAM": "Do not pay through the link. Track the parcel on the courier's official site or app.",
    "OTP_SCAM": "Never share an OTP with anyone — not even someone claiming to be bank staff or support.",
    "DIGITAL_ARREST": "Real police never demand money over video calls. Hang up and call the cyber helpline 1930 or your local police station.",
    "FAKE_SUPPORT": "Do not install remote-access apps or share your screen. Contact support through the company's official channel.",
    "OTHER_SCAM": "Do not pay any upfront fee or share personal details. Verify the offer independently.",
}

DISCLAIMER = (
    "This is an automated assessment based on a small development model and "
    "pattern matching — it is indicative only, not definitive proof of fraud. "
    "When in doubt, verify through an official channel."
)

URL_DISCLAIMER = (
    "This is a static URL assessment based only on the link's structure — it "
    "was not visited or checked against threat-intelligence feeds, so it is "
    "not definitive proof that the destination is malicious or safe."
)


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def build_explanation(category: str, indicators: list[dict], risk_level: str) -> str:
    note = CATEGORY_NOTES.get(category, CATEGORY_NOTES["OTHER_SCAM"])
    if not indicators:
        if category == "NORMAL":
            return (
                "The message contains no scam indicators recognized by the system. "
                "It appears potentially benign, but stay cautious with unknown senders."
            )
        return (
            f"The classifier leaned toward {category_label(category).lower()} because "
            f"{note}, though no individual high-confidence pattern was isolated."
        )
    titles = [i["title"].lower().replace(" detected", "") for i in indicators[:4]]
    joined = "; ".join(titles)
    if risk_level == "HIGH":
        strength = "Several scam indicators were detected"
    elif risk_level == "MEDIUM":
        strength = "Some potentially suspicious signals were found"
    else:
        strength = "Only weak or isolated signals were found"
    return (
        f"{strength}: {joined}. In context, {note}. "
        "These are commonly observed signals, not proof of wrongdoing."
    )


def build_recommendation(category: str, risk_level: str) -> str:
    action = CATEGORY_ACTIONS.get(category, CATEGORY_ACTIONS["OTHER_SCAM"])
    if risk_level == "LOW":
        return action + " You can generally proceed with normal caution."
    if risk_level == "MEDIUM":
        return action + " Pause before acting, and verify the request through an official channel first."
    return action + " Do not click, reply, pay or share sensitive information until verified officially."


def build_url_explanation(signals: list[dict], risk_level: str) -> str:
    if not signals:
        return (
            "No major structural indicators were detected in this URL. That means "
            "the link's shape looks ordinary — it does not establish that the "
            "destination is safe."
        )
    titles = [s["title"].lower() for s in signals[:4]]
    joined = "; ".join(titles)
    strength = (
        "Several risk indicators were detected"
        if risk_level == "HIGH"
        else "Some potentially suspicious signals were found"
        if risk_level == "MEDIUM"
        else "Only minor structural signals were found"
    )
    return (
        f"{strength}: {joined}. These structural patterns can occur in suspicious "
        "links, but they are not individually conclusive and the destination was not visited."
    )


def build_url_recommendation(risk_level: str) -> str:
    base = (
        "Do not enter passwords, OTPs or payment information unless you independently "
        "verify the website through an official source (type the address yourself or use "
        "the organization's official app). Do not click or visit suspicious links merely "
        "to investigate them."
    )
    if risk_level == "LOW":
        return base + " This link shows no major structural warning signs, but caution still applies."
    if risk_level == "MEDIUM":
        return base + " Treat this link as potentially suspicious until verified."
    return base + " This link shows multiple risk indicators — avoid interacting with it."
