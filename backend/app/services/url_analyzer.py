"""Static URL analyzer — parsing + structural signals, NO network access.

Security model: this module uses only stdlib parsing (urllib.parse, re,
ipaddress). It never opens sockets, follows redirects, downloads content,
executes JavaScript, or passes the URL to a shell. Analyzing
``https://suspicious.example/path`` performs zero network requests.

Signals are structural evidence, never proof of maliciousness.
"""

import ipaddress
import re
from urllib.parse import urlsplit

from .brand_config import BRANDS
from .reputation.client import check_domain_reputation

ALLOWED_SCHEMES = {"http", "https"}
REJECTED_SCHEMES = {"javascript", "data", "file", "vbscript", "ftp"}
MAX_URL_LENGTH = 2048

LONG_URL_THRESHOLD = 200
LONG_HOSTNAME_THRESHOLD = 50
MANY_SUBDOMAINS_THRESHOLD = 3

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "rebrand.ly", "cutt.ly", "tiny.cc", "shorturl.at", "rb.gy", "s.id",
}

CREDENTIAL_PATH_WORDS = {
    "login", "verify", "account", "security", "update", "confirm",
    "password", "signin", "sign-in", "banking", "wallet", "recover",
    "unlock", "authenticate",
}

SENSITIVE_QUERY_WORDS = {
    "password", "passwd", "otp", "token", "session", "sessionid",
    "card", "cvv", "pin", "secret",
}

URL_IN_TEXT_RE = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+)", re.IGNORECASE)
TRAILING_PUNCT = ".,;:!?'\")]}"
ENCODED_RE = re.compile(r"%[0-9A-Fa-f]{2}")
HOSTNAME_LABEL_RE = re.compile(r"^(?!-)[A-Za-z0-9\u0080-\U0010FFFF_-]{1,63}(?<!-)$")

MAX_URLS_PER_MESSAGE = 3


def levenshtein(a: str, b: str) -> int:
    """Pure-python edit distance (no extra dependency)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _brand_in_host(hostname: str, brand: str) -> bool:
    return brand in hostname


def _is_genuine_brand_domain(registrable: str, brand: str) -> bool:
    return registrable == brand or registrable.startswith(brand + ".")


def _typosquat_labels(hostname: str, registrable: str, brand: str) -> list[str]:
    """Labels resembling a brand without being its genuine domain."""
    if _is_genuine_brand_domain(registrable, brand):
        return []
    hits = []
    for label in re.split(r"[.\-_]", hostname):
        if len(label) < 4 or len(brand) < 4:
            continue
        if label == brand:
            continue  # handled by BRAND_IMPERSONATION, not typosquat
        dist = levenshtein(label, brand)
        if dist <= 2 or (1 - dist / max(len(label), len(brand))) >= 0.7:
            hits.append(label)
    return hits


def _validate_hostname(hostname: str) -> None:
    """Raise ValueError if the hostname is not structurally plausible."""
    try:
        ipaddress.ip_address(hostname)
        return
    except ValueError:
        pass
    if re.search(r"\s", hostname):
        raise ValueError("Malformed URL: hostname contains whitespace.")
    labels = hostname.split(".")
    if labels != ["localhost"] and len(labels) < 2:
        raise ValueError("Malformed URL: hostname has no domain structure.")
    for label in labels:
        if not HOSTNAME_LABEL_RE.match(label):
            raise ValueError(f"Malformed URL: invalid hostname label '{label}'.")


def parse_url(raw: str) -> dict:
    """Parse + normalize. Raises ValueError with a user-facing message."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("URL must not be empty.")
    if len(text) > MAX_URL_LENGTH:
        raise ValueError(f"URL too long (max {MAX_URL_LENGTH} characters).")

    scheme_given = "://" in text or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", text) is not None
    lowered_scheme = text.split(":", 1)[0].lower() if ":" in text else ""
    if lowered_scheme in REJECTED_SCHEMES:
        raise ValueError(
            f"Unsupported URL scheme '{lowered_scheme}'. Only http and https URLs can be analyzed."
        )

    candidate = text if scheme_given else "http://" + text
    try:
        parts = urlsplit(candidate)
    except ValueError as exc:
        raise ValueError(f"Malformed URL: {exc}") from exc

    scheme = parts.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only http and https URLs can be analyzed.")
    hostname = (parts.hostname or "").lower().rstrip(".")
    if not hostname:
        raise ValueError("Malformed URL: no hostname found.")
    _validate_hostname(hostname)
    try:
        port = parts.port  # raises ValueError on invalid port
    except ValueError as exc:
        raise ValueError(f"Malformed URL: invalid port ({exc}).") from exc

    try:
        punycode = hostname.encode("idna").decode("ascii")
    except Exception:
        punycode = hostname

    labels = hostname.split(".")
    if len(labels) >= 2:
        registrable = ".".join(labels[-2:])
        subdomains = labels[:-2]
    else:
        registrable = hostname
        subdomains = []
    tld = labels[-1] if labels else ""

    uses_ip = False
    is_private_ip = False
    try:
        ip = ipaddress.ip_address(hostname)
        uses_ip = True
        is_private_ip = ip.is_private or ip.is_loopback or ip.is_reserved
    except ValueError:
        pass

    return {
        "input": text,
        "normalized": candidate,
        "scheme": scheme,
        "scheme_given": scheme_given,
        "hostname": hostname,
        "punycode": punycode,
        "registrable": registrable,
        "subdomains": subdomains,
        "tld": tld,
        "path": parts.path or "",
        "query": parts.query or "",
        "fragment": parts.fragment or "",
        "has_userinfo": parts.username is not None,
        "port": port,
        "uses_ip": uses_ip,
        "is_private_ip": is_private_ip,
        "url_length": len(text),
        "hostname_length": len(hostname),
    }


def detect_url_signals(parsed: dict) -> list[dict]:
    """Derive structured signals from parsed URL (static only)."""
    signals: list[dict] = []

    def add(code, severity, title, description):
        signals.append({"code": code, "severity": severity,
                        "title": title, "description": description})

    hostname = parsed["hostname"]
    registrable = parsed["registrable"]

    if parsed["url_length"] > LONG_URL_THRESHOLD:
        add("LONG_URL", "low", "Unusually long URL",
            "The URL is significantly longer than typical URLs. Length alone proves nothing.")
    if parsed["hostname_length"] > LONG_HOSTNAME_THRESHOLD:
        add("LONG_HOSTNAME", "low", "Unusually long hostname",
            "The hostname is much longer than typical hostnames.")
    if len(parsed["subdomains"]) >= MANY_SUBDOMAINS_THRESHOLD:
        add("MANY_SUBDOMAINS", "medium", "Many subdomains",
            f"The URL has {len(parsed['subdomains'])} subdomain levels, which can be used to obscure the real domain.")
    if parsed["uses_ip"]:
        detail = "a private/loopback address" if parsed["is_private_ip"] else "a raw IP address"
        add("IP_HOSTNAME", "high", "IP address used as hostname",
            f"The site is addressed by {detail} instead of a domain name — common in suspicious links, "
            "though IP access also has legitimate uses.")
    if parsed["port"] not in (None, 80, 443):
        add("NON_STANDARD_PORT", "medium", "Non-standard port",
            f"The URL uses port {parsed['port']} instead of the usual web ports (80/443).")
    if hostname in SHORTENERS or registrable in SHORTENERS:
        add("SHORTENED_URL", "medium", "URL shortener detected",
            "Shortened links hide the real destination. The destination was NOT expanded or visited.")
    if parsed["has_userinfo"]:
        add("USERINFO_IN_URL", "high", "Credentials/lookup trick in URL",
            "The URL contains an '@' section before the hostname — a known trick to disguise the real destination.")
    encoded = ENCODED_RE.findall(parsed["normalized"])
    if len(encoded) >= 3 or (encoded and len(encoded) / max(len(parsed["normalized"]), 1) > 0.10):
        add("EXCESSIVE_ENCODING", "medium", "Excessive percent-encoding",
            "The URL contains heavy percent-encoding, which can hide its true structure.")
    path_words = set(re.split(r"[^a-z]+", parsed["path"].lower()))
    if path_words & CREDENTIAL_PATH_WORDS:
        add("SUSPICIOUS_PATH", "medium", "Credential-related path detected",
            "The URL path contains words commonly associated with login or account-verification pages. "
            "Many legitimate sites use these too.")
    for brand in BRANDS:
        if _brand_in_host(hostname, brand) and not _is_genuine_brand_domain(registrable, brand):
            add("BRAND_IMPERSONATION", "high", "Possible brand impersonation pattern",
                f"The address contains '{brand}' but is not the genuine {brand} domain. "
                "This pattern occurs in impersonation attempts, but is not proof of maliciousness.")
            break
    for brand in BRANDS:
        hits = _typosquat_labels(hostname, registrable, brand)
        if hits:
            add("POSSIBLE_TYPOSQUATTING", "high", "Domain resembles a known brand",
                f"'{hits[0]}' closely resembles '{brand}' (possible typosquatting). "
                "Similarity alone does not establish malicious intent.")
            break
    if parsed["query"]:
        qnames = {p.split("=")[0].lower() for p in parsed["query"].split("&")}
        if qnames & SENSITIVE_QUERY_WORDS or len(parsed["query"]) > 200:
            add("SUSPICIOUS_QUERY", "low", "Sensitive-looking query string",
                "The query string references sensitive data or is unusually long. Normal tracking parameters do not trigger this.")
    if parsed["scheme"] == "http":
        add("HTTP_NOT_HTTPS", "low", "Connection is not HTTPS",
            "The link does not use HTTPS. Note: HTTPS alone never proves a site is trustworthy — "
            "many phishing sites use HTTPS.")

    return signals


def analyze_url(raw: str) -> dict:
    """Full static analysis. Returns signals + technical details + reputation stub."""
    from .url_risk_engine import score_url_risk  # local import: avoid cycle

    parsed = parse_url(raw)
    signals = detect_url_signals(parsed)
    risk = score_url_risk(signals)
    reputation = check_domain_reputation(parsed["registrable"])

    return {
        "url": parsed["input"],
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "signals": signals,
        "technical_details": {
            "scheme": parsed["scheme"],
            "hostname": parsed["hostname"],
            "punycode": parsed["punycode"],
            "domain": parsed["registrable"],
            "subdomains": parsed["subdomains"],
            "tld": parsed["tld"],
            "uses_https": parsed["scheme"] == "https",
            "uses_ip_address": parsed["uses_ip"],
            "is_private_ip": parsed["is_private_ip"],
            "port": parsed["port"],
            "url_length": parsed["url_length"],
            "hostname_length": parsed["hostname_length"],
        },
        "reputation": reputation,
    }


def extract_urls_from_text(text: str, limit: int = MAX_URLS_PER_MESSAGE) -> list[str]:
    """Find candidate URLs in a message (regex only — nothing is fetched)."""
    if not text:
        return []
    found = []
    for match in URL_IN_TEXT_RE.finditer(text):
        url = match.group(0).rstrip(TRAILING_PUNCT)
        if url and url not in found:
            found.append(url)
        if len(found) >= limit:
            break
    return found
