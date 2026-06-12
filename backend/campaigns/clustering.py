"""Spam and bulk-marketing campaign detection via message clustering."""

import re

from sms_analysis.models import SMSMessage

from .models import Campaign

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'for', 'of', 'in', 'on',
    'your', 'you', 'and', 'or', 'this', 'that', 'it', 'be', 'has', 'have', 'will',
    'our', 'get', 'via', 'not', 'out', 'can', 'all', 'any', 'may', 'its',
}

TEMPLATE_PATTERN = re.compile(r'\{\{[^}]+\}\}')
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
NUMBER_PATTERN = re.compile(r'\b\d+\b')

MARKETING_SIGNALS = [
    'reply stop', 'opt out', 'unsubscribe', 'limited time', 'sitewide',
    'sale is live', 'shop now', 'reply yes', 'seasonal sale', 'biggest sale',
    'don\'t miss', 'hours only', 't&c apply', 'direct link', 'off sitewide',
    'click here', 'offer expires', 'act now', 'free shipping', 'promo code',
]


def _normalize_message(text: str) -> str:
    """Normalize templates, URLs, and numbers so similar bulk SMS cluster together."""
    text = text.lower()
    text = TEMPLATE_PATTERN.sub(' tplvar ', text)
    text = URL_PATTERN.sub(' urllink ', text)
    text = NUMBER_PATTERN.sub(' num ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _message_fingerprint(text: str) -> str:
    return _normalize_message(text)


def _extract_signature(text: str) -> frozenset:
    """Keyword signature from normalized message text."""
    words = re.findall(r'[a-z]{3,}', _normalize_message(text))
    keywords = [w for w in words if w not in STOPWORDS and w not in ('tplvar', 'urllink', 'num')]
    return frozenset(keywords[:12])


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def is_bulk_campaign_message(text: str) -> bool:
    """Detect template-based or bulk marketing/promotional SMS."""
    if TEMPLATE_PATTERN.search(text):
        return True

    text_lower = text.lower()
    signal_count = sum(1 for signal in MARKETING_SIGNALS if signal in text_lower)
    return signal_count >= 2


def _campaign_type_for_messages(messages: list) -> str:
    fraud_types = [m.fraud_type for m in messages if m.fraud_type]
    if fraud_types:
        return 'scam'

    if any(is_bulk_campaign_message(m.message) for m in messages):
        return 'marketing'

    spam_count = sum(1 for m in messages if m.prediction == 'spam')
    if spam_count >= len(messages) / 2:
        return 'spam'

    return 'promotional'


def _risk_level(score: float) -> str:
    if score >= 85:
        return 'critical'
    if score >= 70:
        return 'high'
    if score >= 50:
        return 'medium'
    return 'low'


def _campaign_slug(text: str) -> str:
    normalized = _normalize_message(text)
    words = [
        w for w in normalized.split()
        if w not in STOPWORDS and w not in ('tplvar', 'urllink', 'num')
    ]
    return ' '.join(w.capitalize() for w in words[:5]) or 'Bulk SMS'


def _build_campaign_name(representative_text: str, campaign_type: str) -> str:
    """Stable campaign name from normalized content (same message → same name)."""
    slug = _campaign_slug(representative_text)

    if campaign_type == 'marketing':
        if TEMPLATE_PATTERN.search(representative_text):
            return f'Campaign: Marketing — {slug}'
        return f'Campaign: Promotional — {slug}'

    if campaign_type == 'scam':
        return f'Campaign: Scam — {slug}'

    return f'Campaign: {slug}'


def _unique_sample_messages(messages: list, limit: int = 3) -> list[str]:
    """Return unique sample texts (no duplicate previews)."""
    seen = set()
    samples = []
    for sms in messages:
        fp = _message_fingerprint(sms.message)
        if fp in seen:
            continue
        seen.add(fp)
        samples.append(sms.message[:150])
        if len(samples) >= limit:
            break
    return samples


def _dedupe_candidates(candidates: list) -> list[dict]:
    """
    Merge identical analyzed messages into one entry with occurrence count.
    Prevents the same SMS text from inflating clusters or sample lists.
    """
    grouped: dict[str, dict] = {}

    for sms in candidates:
        fp = _message_fingerprint(sms.message)
        if fp not in grouped:
            grouped[fp] = {
                'sms': sms,
                'count': 0,
                'user_ids': set(),
            }
        grouped[fp]['count'] += 1
        if sms.user_id:
            grouped[fp]['user_ids'].add(sms.user_id)

    return list(grouped.values())


def _cluster_deduped(entries: list[dict], similarity_threshold: float = 0.38) -> list[list[dict]]:
    """Group deduplicated message entries by similar content."""
    if not entries:
        return []

    signatures = [_extract_signature(e['sms'].message) for e in entries]
    clusters: list[list[dict]] = []

    for idx, entry in enumerate(entries):
        sig = signatures[idx]
        sms = entry['sms']
        if len(sig) < 2 and not is_bulk_campaign_message(sms.message):
            continue

        placed = False
        for cluster in clusters:
            rep_idx = entries.index(cluster[0])
            if _jaccard(sig, signatures[rep_idx]) >= similarity_threshold:
                cluster.append(entry)
                placed = True
                break

        if not placed:
            clusters.append([entry])

    return clusters


def _get_campaign_candidates(limit: int = 500) -> list:
    """Messages eligible for campaign clustering."""
    recent = list(SMSMessage.objects.order_by('-timestamp')[:limit])
    return [
        sms for sms in recent
        if sms.prediction == 'spam' or is_bulk_campaign_message(sms.message)
    ]


def _merge_overlapping_clusters(clusters: list[list[dict]], threshold: float = 0.5) -> list[list[dict]]:
    """Merge clusters that share similar representative messages."""
    if len(clusters) <= 1:
        return clusters

    merged: list[list[dict]] = []
    used = [False] * len(clusters)

    for i, cluster_a in enumerate(clusters):
        if used[i]:
            continue

        combined = list(cluster_a)
        rep_a = _extract_signature(cluster_a[0]['sms'].message)

        for j in range(i + 1, len(clusters)):
            if used[j]:
                continue
            rep_b = _extract_signature(clusters[j][0]['sms'].message)
            if _jaccard(rep_a, rep_b) >= threshold:
                combined.extend(clusters[j])
                used[j] = True

        merged.append(combined)
        used[i] = True

    return merged


def detect_campaigns(min_cluster_size: int = 2) -> list:
    """Cluster similar spam/marketing messages into campaigns."""
    candidates = _get_campaign_candidates()
    deduped = _dedupe_candidates(candidates)
    clusters = _cluster_deduped(deduped)
    clusters = _merge_overlapping_clusters(clusters)

    Campaign.objects.update(is_active=False)
    campaigns_created = []

    for cluster in clusters:
        is_template_cluster = any(is_bulk_campaign_message(e['sms'].message) for e in cluster)
        total_messages = sum(e['count'] for e in cluster)

        if total_messages < min_cluster_size and not is_template_cluster:
            continue

        representative = cluster[0]['sms']
        rep_text = representative.message

        signatures = [_extract_signature(e['sms'].message) for e in cluster]
        keywords = sorted(set().union(*signatures))[:5] if signatures else []

        user_ids = set()
        for entry in cluster:
            user_ids.update(entry['user_ids'])

        all_sms = [e['sms'] for e in cluster]
        avg_confidence = sum(e['sms'].confidence for e in cluster) / len(cluster)
        risk_score = min(max(avg_confidence, 0.55 if is_template_cluster else 0.0) * 100, 100)
        campaign_type = _campaign_type_for_messages(all_sms)
        campaign_name = _build_campaign_name(rep_text, campaign_type)

        campaign, _ = Campaign.objects.update_or_create(
            campaign_name=campaign_name,
            defaults={
                'cluster_keywords': keywords,
                'sample_messages': _unique_sample_messages(all_sms, limit=3),
                'affected_users': len(user_ids) or total_messages,
                'message_count': total_messages,
                'risk_score': round(risk_score, 1),
                'risk_level': _risk_level(risk_score),
                'campaign_type': campaign_type,
                'is_active': True,
            },
        )
        campaigns_created.append(campaign)

    return campaigns_created
