"""SMS Security Score generation (0-100, lower = more dangerous)."""

URGENCY_WORDS = [
    'urgent', 'immediately', 'now', 'hurry', 'limited', 'expire', 'last chance',
    'act now', 'today only', 'within 24 hours', 'deadline',
]

FINANCIAL_WORDS = [
    'money', 'cash', 'payment', 'transfer', 'bank', 'account', 'wallet',
    '₹', 'rs', 'rupee', 'credit', 'debit', 'loan', 'invest',
]

SUSPICIOUS_WORDS = [
    'free', 'winner', 'prize', 'congratulations', 'claim', 'click', 'verify',
    'otp', 'kyc', 'blocked', 'suspended', 'reward', 'lottery',
]


def calculate_security_score(
    text: str,
    prediction: str,
    confidence: float,
    phishing_risk: float,
    fraud_detected: bool,
    suspicious_words: list,
) -> dict:
    """
    Generate security score 0-100.
    Higher score = safer message.
    """
    text_lower = text.lower()
    score = 100
    reasons = []

    if prediction == 'spam':
        penalty = int(confidence * 40)
        score -= penalty
        reasons.append(f'Classified as spam ({confidence:.0%} confidence)')

    if phishing_risk > 0:
        penalty = int(phishing_risk * 0.35)
        score -= penalty
        reasons.append('Suspicious link detected')

    if fraud_detected:
        score -= 25
        reasons.append('Financial/scam fraud pattern detected')

    urgency_count = sum(1 for w in URGENCY_WORDS if w in text_lower)
    if urgency_count > 0:
        penalty = min(urgency_count * 8, 20)
        score -= penalty
        reasons.append('Urgency language detected')

    financial_count = sum(1 for w in FINANCIAL_WORDS if w in text_lower)
    if financial_count > 0:
        penalty = min(financial_count * 6, 18)
        score -= penalty
        reasons.append('Financial request keywords')

    if suspicious_words:
        penalty = min(len(suspicious_words) * 5, 15)
        score -= penalty
        if not any('spam' in r for r in reasons):
            reasons.append(f'Suspicious words: {", ".join(suspicious_words[:3])}')

    score = max(0, min(100, score))

    if score >= 70:
        level = 'Safe'
    elif score >= 40:
        level = 'Moderate Risk'
    else:
        level = 'High Risk'

    return {
        'security_score': score,
        'risk_level': level,
        'reasons': reasons,
    }
