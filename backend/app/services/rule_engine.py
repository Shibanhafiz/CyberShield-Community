"""Rule-based indicator detection.

Indicators are EVIDENCE/SIGNALS, not proof of malicious intent. Each match
produces a structured {code, severity, title, description} dict. At most one
indicator per code fires per message.

Severity guide: high = direct request for secrets/money or explicit threat;
medium = pressure, impersonation or payment-adjacent language; low = context
that only matters combined with other signals.
"""

import re

# Each rule: (code, severity, title, description, [regexes])
RULES: list[tuple] = [
    (
        "URGENT_LANGUAGE", "medium",
        "Urgency language detected",
        "The message pressures the recipient to act immediately. Genuine urgent "
        "notices exist, so this is only one signal among several.",
        [r"\burgent\b", r"\bimmediately\b", r"\bright now\b", r"within \d+ ?hours?",
         r"today only", r"last warning", r"final notice", r"\bhurry\b", r"act now",
         r"expires? (today|tonight)", r"offer ends", r"registration closes", r"limited (slots|time|offer)"],
    ),
    (
        "THREAT_LANGUAGE", "medium",
        "Threatening language detected",
        "The message threatens account closure, arrest or penalties to create fear.",
        [r"will be (blocked|suspended|deleted|deactivated|closed|frozen|cut)",
         r"face (arrest|jail|legal action)", r"police will", r"avoid (jail|penalty|disconnection)",
         r"or it will be returned", r"or face arrest"],
    ),
    (
        "ACCOUNT_SUSPENSION", "high",
        "Account suspension claim detected",
        "The message claims an account, card, KYC or service is blocked or expiring — "
        "a common pretext for phishing.",
        [r"account .* (blocked|suspended|frozen|closed|locked|disabled)",
         r"kyc .* (pending|expired|suspended)", r"sim .* deactivat",
         r"card .* blocked", r"login is disabled", r"number will be banned",
         r"aadhaar .* deactivat", r"pan .* blocked"],
    ),
    (
        "OTP_REQUEST", "high",
        "OTP request detected",
        "The message asks for a one-time password. Legitimate organizations never "
        "ask for OTPs over calls, SMS or chat.",
        [r"(share|send|tell|forward|enter|read out|confirm|approve).{0,40}\botp\b",
         r"\botp\b.{0,40}(share|required|needed|confirm|verification)",
         r"6-digit code", r"\botp\b.{0,20}screen"],
    ),
    (
        "PASSWORD_REQUEST", "high",
        "Password/login request detected",
        "The message seeks login credentials. These should only ever be entered on "
        "an official website or app you opened yourself.",
        [r"\bpassword\b", r"username and password", r"internet banking (password|login)",
         r"confirm your .* login"],
    ),
    (
        "PIN_REQUEST", "high",
        "PIN/CVV/card request detected",
        "The message seeks a PIN, CVV or card details. Never share these with anyone.",
        [r"\bpin\b", r"\bcvv\b", r"card (details|number)", r"debit card .* ready",
         r"keep your debit card"],
    ),
    (
        "CREDENTIAL_REQUEST", "high",
        "Sensitive information request detected",
        "The message asks for identity or account details (Aadhaar, account numbers, "
        "screen access) that can enable fraud.",
        [r"aadhaar (number|copy|details)", r"account details", r"share your screen",
         r"grant remote access", r"remote access"],
    ),
    (
        "FINANCIAL_REQUEST", "medium",
        "Payment or money-transfer request detected",
        "The message requests a payment, fee or transfer. Small advance fees are a "
        "hallmark of many scam types.",
        [r"pay (rs|₹|\$)?\s?\d", r"transfer (money|funds|rs)", r"\bdeposit\b",
         r"(registration|joining|processing|security|token|verification|release|file|membership).{0,20}(fee|charge|amount|fee)",
         r"(fee|charge) of rs", r"\bupi\b", r"collect request", r"recharge my phone",
         r"token advance", r"membership fee"],
    ),
    (
        "PRIZE_CLAIM", "medium",
        "Prize/lottery claim detected",
        "The message claims the recipient won something. Genuine lotteries never ask "
        "winners to pay fees upfront.",
        [r"\bwon\b", r"\bwinner\b", r"\blottery\b", r"lucky draw", r"\bprize\b",
         r"selected for verification", r"cashback"],
    ),
    (
        "INVESTMENT_PROMISE", "high",
        "Unrealistic investment promise detected",
        "The message guarantees high returns with little or no risk — a classic "
        "investment-fraud pattern.",
        [r"guaranteed? .{0,20}returns?", r"\d+x .{0,10}profit", r"double your money",
         r"risk-free", r"\d+\s?% .{0,20}(return|profit|accuracy|daily profit)",
         r"pre-ipo", r"\d00% returns"],
    ),
    (
        "JOB_PROMISE", "high",
        "Job offer with upfront payment detected",
        "The message offers easy income but demands an advance fee. Genuine employers "
        "never charge candidates to join.",
        [r"work.from.home", r"data entry", r"typing job", r"task job",
         r"earn rs.{0,30}per (month|week|day)", r"selected for .{0,20}(job|role)",
         r"joining fee", r"i am hr from", r"government job placement",
         r"guaranteed income", r"guaranteed .{0,10}placement"],
    ),
    (
        "IMPERSONATION", "medium",
        "Possible authority/brand impersonation",
        "The message invokes a bank, government body or well-known brand. Scammers "
        "borrow trusted names; verify via the official channel.",
        [r"\bsbi\b", r"\bhdfc\b", r"\bpnb\b", r"\bicici\b", r"\baxis\b", r"\brbi\b",
         r"\bcbi\b", r"\bpolice\b", r"cyber ?(crime|cell)", r"\bed\b.{0,10}investigation",
         r"\btrai\b", r"supreme court", r"narcotics", r"\bcourt\b.{0,10}order",
         r"microsoft", r"\bamazon\b", r"google ?pay", r"\bpaytm\b", r"\bphonepe\b",
         r"whatsapp support", r"electricity (board|department)", r"india post",
         r"bluedart", r"fedex", r"\bkbc\b", r"\bsebi\b",
         r"(officer|manager|agent|helpline|support|customs).{0,20}(calling|speaking|here|department)"],
    ),
    (
        "SUSPICIOUS_URL", "high",
        "Suspicious link detected",
        "The message contains a link, possibly shortened or on an unusual domain. "
        "Do not open it directly; check the sender independently.",
        [r"https?://", r"www\.", r"bit\.ly", r"tinyurl", r"\.(tk|ml|ga|gq|cf|xyz|top|buzz)\b",
         r"click (here|to|this link)", r"login here", r"verify.{0,20}http"],
    ),
    (
        "EXTERNAL_CONTACT_REQUEST", "low",
        "Request to move conversation detected",
        "The message tries to move contact to another app, remote-access tool or "
        "private channel — a common control tactic.",
        [r"\bwhatsapp\b", r"\btelegram\b", r"\bskype\b", r"teamviewer",
         r"quicksupport", r"download .{0,20}app", r"stay on .{0,15}(video|voice|skype|camera)",
         r"do not disconnect", r"do not tell anyone", r"remain on camera",
         r"install this app", r"video call"],
    ),
    (
        "LEGAL_THREAT", "high",
        "Legal/police threat detected",
        "The message accuses the recipient of a crime and demands money or "
        "compliance. Real agencies do not demand payment over calls or video chat.",
        [r"digital arrest", r"under investigation", r"money laundering",
         r"criminal case", r"arrest (you|within|in \d)", r"illegal drugs",
         r"drugs.{0,20}courier", r"court order", r"son is in custody",
         r"bank accounts are frozen", r"linked to a criminal case",
         r"objectionable content", r"penalty now or face arrest"],
    ),
    (
        "DELIVERY_ISSUE", "medium",
        "Parcel/delivery problem claim detected",
        "The message claims a parcel is stuck and demands a small fee — typical of "
        "fake delivery notices.",
        [r"(parcel|package|courier|shipment|delivery|consignment).{0,30}(held|stuck|delayed|failed|pending|incomplete|expired|returned)",
         r"customs duty", r"redelivery", r"address (verification|is incomplete)",
         r"shipping insurance", r"out for delivery", r"locker code"],
    ),
]

_COMPILED = [
    (code, sev, title, desc, [re.compile(p, re.IGNORECASE) for p in patterns])
    for code, sev, title, desc, patterns in RULES
]


def detect_indicators(text: str) -> list[dict]:
    """Scan text and return fired indicators (max one per code)."""
    found: list[dict] = []
    if not text or not text.strip():
        return found
    for code, severity, title, description, patterns in _COMPILED:
        if any(p.search(text) for p in patterns):
            found.append(
                {"code": code, "severity": severity, "title": title,
                 "description": description}
            )
    return found


# Fallback category mapping when the ML model is unavailable.
FALLBACK_CATEGORY_MAP: list[tuple] = [
    ("OTP_REQUEST", "OTP_SCAM"),
    ("LEGAL_THREAT", "DIGITAL_ARREST"),
    ("JOB_PROMISE", "JOB_SCAM"),
    ("INVESTMENT_PROMISE", "INVESTMENT_SCAM"),
    ("ACCOUNT_SUSPENSION", "BANKING_SCAM"),
    ("DELIVERY_ISSUE", "DELIVERY_SCAM"),
    ("PASSWORD_REQUEST", "PHISHING"),
    ("CREDENTIAL_REQUEST", "PHISHING"),
    ("SUSPICIOUS_URL", "PHISHING"),
    ("PRIZE_CLAIM", "OTHER_SCAM"),
    ("FINANCIAL_REQUEST", "OTHER_SCAM"),
]


def fallback_category(indicators: list[dict]) -> str:
    codes = {i["code"] for i in indicators}
    for code, category in FALLBACK_CATEGORY_MAP:
        if code in codes:
            return category
    if indicators:
        return "OTHER_SCAM"
    return "NORMAL"
