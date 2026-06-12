"""Fraud pattern detection for SMS messages."""

import re

FRAUD_PATTERNS = {
    'banking_fraud': {
        'patterns': [
            r'\bkyc\b', r'account\s*(blocked|suspended|locked)', r'\botp\b',
            r'bank\s*account', r'update\s*your\s*(account|details|kyc)',
            r'debit\s*card', r'credit\s*card', r'net\s*banking',
            r'immediately\s*verify', r'account\s*will\s*be\s*closed',
        ],
        'keywords': ['kyc', 'otp', 'account blocked', 'verify account', 'bank'],
    },
    'lottery_scam': {
        'patterns': [
            r'won\s*(a\s*)?(prize|lottery|reward|₹|rs\.?)',
            r'congratulations.*won', r'you\s*(have\s*)?won',
            r'claim\s*your\s*(prize|reward|money)', r'₹\s*[\d,]+',
            r'rs\.?\s*[\d,]+', r'lakh', r'crore',
        ],
        'keywords': ['won', 'prize', 'lottery', 'congratulations', 'claim'],
    },
    'fake_job_scam': {
        'patterns': [
            r'earn\s*₹?\s*[\d,]+\s*/?\s*day', r'work\s*from\s*home',
            r'part\s*time\s*job', r'daily\s*income', r'no\s*experience',
            r'whatsapp\s*job', r'data\s*entry\s*job',
        ],
        'keywords': ['earn', 'work from home', 'daily income', 'job offer'],
    },
    'investment_scam': {
        'patterns': [
            r'double\s*(your\s*)?money', r'guaranteed\s*returns?',
            r'\d+%\s*(daily|monthly|profit)', r'crypto\s*investment',
            r'trading\s*scheme', r'get\s*rich', r'forex\s*trading',
        ],
        'keywords': ['double money', 'guaranteed returns', 'investment', 'profit'],
    },
    'wallet_scam': {
        'patterns': [
            r'transfer\s*received', r'amount\s*available', r'your\s*wallet',
            r'wallet\s*balance', r'credited\s*to', r'check\s*now',
            r'drop\s*for\s*account', r'available\s*in\s*your\s*wallet',
            r'received\s*:\s*rs', r'transfer\s*received\s*:',
        ],
        'keywords': ['wallet', 'transfer received', 'check now', 'amount available'],
    },
}

FRAUD_LABELS = {
    'banking_fraud': 'Banking Fraud',
    'lottery_scam': 'Lottery Scam',
    'fake_job_scam': 'Fake Job Scam',
    'investment_scam': 'Investment Scam',
    'wallet_scam': 'Wallet Scam',
}


def detect_fraud(text: str) -> dict:
    """Detect fraud type from SMS text."""
    text_lower = text.lower()
    matches = []

    for fraud_type, config in FRAUD_PATTERNS.items():
        score = 0
        matched_patterns = []

        for pattern in config['patterns']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1
                matched_patterns.append(pattern)

        for kw in config['keywords']:
            if kw.lower() in text_lower:
                score += 0.5

        if score > 0:
            matches.append({
                'type': fraud_type,
                'label': FRAUD_LABELS[fraud_type],
                'score': score,
                'matched_patterns': len(matched_patterns),
            })

    if not matches:
        return {'fraud_type': None, 'fraud_label': None, 'confidence': 0, 'all_matches': []}

    best = max(matches, key=lambda x: x['score'])
    confidence = min(best['score'] / 3.0, 1.0)

    return {
        'fraud_type': best['type'],
        'fraud_label': best['label'],
        'confidence': round(confidence, 2),
        'all_matches': matches,
    }
