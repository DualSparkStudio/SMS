"""Phishing URL detection module."""

import re
from urllib.parse import urlparse

import tldextract

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'confirm', 'banking',
    'paypal', 'amazon', 'freegift', 'reward', 'claim', 'urgent', 'kyc',
    'otp', 'wallet', 'prize', 'winner', 'cashback',
]

FAKE_DOMAIN_PATTERNS = [
    r'paypal[-_]?(security|login|verify)',
    r'amazon[-_]?(free|gift|reward)',
    r'(sbi|hdfc|icici|axis)[-_]?(secure|login|kyc)',
    r'gov[-_]?(reward|scheme)',
]

URL_PATTERN = re.compile(
    r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}[^\s]*'
)

URL_SHORTENERS = (
    'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd',
    'buff.ly', 'rb.gy', 'cutt.ly', 'shorturl.at', 'rebrand.ly',
)

FINANCIAL_URL_KEYWORDS = (
    'wallet', 'transfer', 'account', 'payment', 'bank', 'credited',
    'received', 'rs', 'amount', 'check', 'verify', 'claim',
)


def extract_urls(text: str) -> list[str]:
    return URL_PATTERN.findall(text)


def analyze_url(url: str) -> dict:
    """Analyze a single URL for phishing indicators."""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed = urlparse(url)
    domain_info = tldextract.extract(url)
    domain = f'{domain_info.domain}.{domain_info.suffix}'
    full_domain = f'{domain_info.subdomain}.{domain}' if domain_info.subdomain else domain

    risk_factors = []
    risk_score = 0

    url_length = len(url)
    if url_length > 75:
        risk_score += 20
        risk_factors.append('Unusually long URL')

    if url_length > 100:
        risk_score += 15
        risk_factors.append('Very long URL (obfuscation)')

    subdomain = domain_info.subdomain.lower()
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in subdomain or kw in domain_info.domain.lower():
            risk_score += 15
            risk_factors.append(f'Suspicious keyword: {kw}')

    for pattern in FAKE_DOMAIN_PATTERNS:
        if re.search(pattern, full_domain, re.IGNORECASE):
            risk_score += 30
            risk_factors.append(f'Fake domain pattern detected')

    if domain_info.suffix in ('xyz', 'top', 'club', 'work', 'click', 'link'):
        risk_score += 20
        risk_factors.append(f'Suspicious TLD: .{domain_info.suffix}')

    if domain_info.subdomain.count('.') >= 2:
        risk_score += 15
        risk_factors.append('Multiple subdomains (phishing technique)')

    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        risk_score += 25
        risk_factors.append('IP address used instead of domain')

    host = full_domain.lower()
    if any(shortener in host for shortener in URL_SHORTENERS):
        risk_score += 40
        risk_factors.append('URL shortener (common in smishing/phishing)')

    risk_score = min(risk_score, 100)
    status = 'dangerous' if risk_score >= 50 else 'safe' if risk_score < 25 else 'suspicious'

    return {
        'url': url,
        'domain': full_domain,
        'status': status,
        'risk_percentage': risk_score,
        'risk_factors': risk_factors,
        'url_length': url_length,
    }


def analyze_urls_in_text(text: str) -> dict:
    urls = extract_urls(text)
    if not urls:
        return {
            'urls_found': [],
            'overall_status': 'safe',
            'max_risk': 0,
            'analyses': [],
        }

    text_lower = text.lower()
    has_financial_context = any(kw in text_lower for kw in FINANCIAL_URL_KEYWORDS)

    analyses = []
    for u in urls:
        analysis = analyze_url(u)
        host = analysis.get('domain', '').lower()
        if has_financial_context and any(s in host for s in URL_SHORTENERS):
            analysis['risk_percentage'] = min(analysis['risk_percentage'] + 25, 100)
            if 'Financial lure combined with shortened URL' not in analysis['risk_factors']:
                analysis['risk_factors'].append('Financial lure combined with shortened URL')
            if analysis['risk_percentage'] >= 50:
                analysis['status'] = 'dangerous'
            elif analysis['risk_percentage'] >= 25:
                analysis['status'] = 'suspicious'
        analyses.append(analysis)

    max_risk = max(a['risk_percentage'] for a in analyses)
    overall = 'dangerous' if max_risk >= 50 else 'suspicious' if max_risk >= 25 else 'safe'

    return {
        'urls_found': urls,
        'overall_status': overall,
        'max_risk': max_risk,
        'analyses': analyses,
    }
