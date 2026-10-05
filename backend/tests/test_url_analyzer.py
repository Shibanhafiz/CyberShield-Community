"""URL analyzer unit tests: spec cases 1-10 + security + static-only proof."""

import pytest

from app.services.url_analyzer import (
    analyze_url,
    detect_url_signals,
    extract_urls_from_text,
    parse_url,
)
from app.services.url_risk_engine import score_url_risk


def codes(raw):
    return {s["code"] for s in detect_url_signals(parse_url(raw))}


def test_1_benign_url_has_few_or_no_signals():
    signals = detect_url_signals(parse_url("https://www.google.com"))
    assert signals == []
    assert score_url_risk(signals)["risk_level"] == "LOW"


def test_2_ip_hostname():
    assert "IP_HOSTNAME" in codes("http://192.168.1.10/login")


def test_3_credential_path():
    assert "SUSPICIOUS_PATH" in codes("https://login.example.com/verify-account")


def test_4_typosquat_brand():
    c = codes("https://paypa1-example.com/login")
    assert "POSSIBLE_TYPOSQUATTING" in c or "BRAND_IMPERSONATION" in c


def test_4b_brand_keyword_combo():
    assert "BRAND_IMPERSONATION" in codes("https://secure-paypal-login-example.com")


def test_4c_genuine_brand_domain_not_flagged():
    c = codes("https://www.paypal.com/signin")
    assert "BRAND_IMPERSONATION" not in c
    assert "POSSIBLE_TYPOSQUATTING" not in c


def test_5_very_long_url():
    assert "LONG_URL" in codes("https://example.com/" + "a" * 250)


def test_6_many_subdomains():
    assert "MANY_SUBDOMAINS" in codes("https://a.b.c.d.example.com/login")


def test_7_malformed_url_rejected():
    with pytest.raises(ValueError):
        parse_url("not a url at all !!!")
    with pytest.raises(ValueError):
        parse_url("https://")


def test_8_encoded_characters():
    assert "EXCESSIVE_ENCODING" in codes("https://example.com/%41%42%43%44%45/login")


def test_9_normal_query_not_flagged():
    c = codes("https://example.com/search?q=hello&page=2")
    assert "SUSPICIOUS_QUERY" not in c
    assert c == set()


def test_10_https_recognized_but_not_proof_of_safety():
    parsed = parse_url("https://example.com/login")
    assert parsed["scheme"] == "https"
    # HTTPS phishing-style URL still gets structural signals, never a clean bill
    c = codes("https://example.com/login")
    assert "HTTP_NOT_HTTPS" not in c
    assert "SUSPICIOUS_PATH" in c


def test_http_flagged_as_signal_not_verdict():
    assert "HTTP_NOT_HTTPS" in codes("http://example.com/")


def test_shortener_detected_but_not_expanded():
    assert "SHORTENED_URL" in codes("https://bit.ly/abc123")


def test_userinfo_trick():
    assert "USERINFO_IN_URL" in codes("http://google.com@evil-example.com/")


def test_nonstandard_port():
    assert "NON_STANDARD_PORT" in codes("https://example.com:8443/login")


def test_scheme_less_accepted():
    parsed = parse_url("www.example.com/login")
    assert parsed["hostname"] == "www.example.com"


def test_rejected_schemes():
    for bad in ("javascript:alert(1)", "data:text/html,hi", "file:///etc/passwd",
                "vbscript:msgbox(1)", "ftp://example.com/x"):
        with pytest.raises(ValueError):
            parse_url(bad)


def test_empty_and_oversize_rejected():
    with pytest.raises(ValueError):
        parse_url("")
    with pytest.raises(ValueError):
        parse_url("https://example.com/" + "x" * 3000)


def test_private_ip_noted():
    signals = detect_url_signals(parse_url("http://127.0.0.1:8000/admin"))
    by_code = {s["code"]: s for s in signals}
    assert "IP_HOSTNAME" in by_code
    assert "NON_STANDARD_PORT" in by_code


def test_unicode_domain_parses():
    parsed = parse_url("https://münchen.example/")
    assert parsed["hostname"] == "münchen.example"
    assert "xn--" in parsed["punycode"]


def test_no_network_access_during_analysis(monkeypatch):
    import socket

    def blocked(*args, **kwargs):
        raise AssertionError("URL analyzer attempted network access!")

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket, "gethostbyname", blocked)
    result = analyze_url("https://paypa1-example.com/login?token=abc")
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")


def test_reputation_adapter_honest():
    result = analyze_url("https://www.google.com")
    assert result["reputation"]["available"] is False
    assert result["reputation"]["source"] is None


def test_extract_urls_from_text():
    text = "Hi, verify here https://evil-example.tk/login and also www.example.com/a, thanks!"
    found = extract_urls_from_text(text)
    assert found == ["https://evil-example.tk/login", "www.example.com/a"]
    assert extract_urls_from_text("no links here") == []
