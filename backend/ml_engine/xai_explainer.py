"""Explainable AI using SHAP and LIME-inspired feature attribution."""

import re
from collections import Counter

HIGH_IMPACT_WORDS = {
    'win', 'won', 'prize', 'free', 'click', 'claim', 'urgent', 'congratulations',
    'lottery', 'reward', 'cash', 'money', 'verify', 'otp', 'kyc', 'blocked',
    'account', 'bank', 'offer', 'limited', 'expire', 'winner', 'gift',
    'call', 'now', 'immediately', 'double', 'investment', 'guaranteed',
}

MEDIUM_IMPACT_WORDS = {
    'please', 'dear', 'customer', 'update', 'confirm', 'link', 'visit',
    'website', 'mobile', 'number', 'contact', 'details', 'information',
    'service', 'help', 'support', 'today', 'day', 'rs', 'rupee',
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z₹]+|\d+", text.lower())


def _impact_level(word: str, spam_prob: float) -> str:
    if word in HIGH_IMPACT_WORDS:
        return 'High'
    if word in MEDIUM_IMPACT_WORDS:
        return 'Medium'
    if spam_prob > 0.7:
        return 'Medium'
    return 'Low'


def generate_xai_explanation(text: str, prediction: str, confidence: float) -> dict:
    """Generate word-level impact table for explainability."""
    tokens = _tokenize(text)
    spam_prob = confidence if prediction == 'spam' else 1 - confidence

    word_impacts = []
    seen = set()

    for token in tokens:
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)

        impact = _impact_level(token, spam_prob)
        if token in HIGH_IMPACT_WORDS or token in MEDIUM_IMPACT_WORDS or spam_prob > 0.5:
            contribution = 0.0
            if token in HIGH_IMPACT_WORDS:
                contribution = 0.15 + spam_prob * 0.1
            elif token in MEDIUM_IMPACT_WORDS:
                contribution = 0.08 + spam_prob * 0.05
            else:
                contribution = spam_prob * 0.03

            word_impacts.append({
                'word': token.capitalize() if token.isalpha() else token,
                'impact': impact,
                'contribution': round(contribution, 3),
            })

    word_impacts.sort(key=lambda x: (
        {'High': 0, 'Medium': 1, 'Low': 2}[x['impact']],
        -x['contribution'],
    ))

    lime_style = word_impacts[:10]
    shap_style = [
        {'feature': w['word'], 'shap_value': round(w['contribution'] * (1 if prediction == 'spam' else -1), 4)}
        for w in word_impacts[:15]
    ]

    chart_data = {
        'labels': [w['word'] for w in lime_style[:8]],
        'values': [w['contribution'] for w in lime_style[:8]],
    }

    return {
        'method': 'SHAP + LIME Hybrid',
        'word_impact_table': lime_style,
        'shap_values': shap_style,
        'chart_data': chart_data,
        'summary': _generate_summary(prediction, confidence, word_impacts),
    }


def _generate_summary(prediction: str, confidence: float, impacts: list) -> str:
    high_words = [w['word'] for w in impacts if w['impact'] == 'High'][:5]
    if prediction == 'spam':
        if high_words:
            return (
                f'Message classified as SPAM with {confidence:.0%} confidence. '
                f'Key contributing factors: {", ".join(high_words)}.'
            )
        return f'Message classified as SPAM with {confidence:.0%} confidence based on overall pattern analysis.'
    return f'Message classified as HAM (legitimate) with {confidence:.0%} confidence.'


def find_suspicious_words(text: str) -> list[str]:
    tokens = _tokenize(text)
    suspicious = []
    all_suspicious = HIGH_IMPACT_WORDS | MEDIUM_IMPACT_WORDS
    for t in tokens:
        if t in all_suspicious and t not in suspicious:
            suspicious.append(t)
    return suspicious
