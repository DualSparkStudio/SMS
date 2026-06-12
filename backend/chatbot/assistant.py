"""AI Chat Assistant — LLM-powered with rule-based fallback."""

from .llm_service import chat_with_llm, is_llm_configured


def generate_chat_response(
    message: str,
    context: dict | None = None,
    history: list | None = None,
) -> dict:
    """Generate conversational response using LLM, with fallback if no API key."""
    context = context or {}
    history = history or []

    llm_result = chat_with_llm(message, history=history, context=context)
    if llm_result:
        return llm_result

    return _fallback_response(message, context)


def _fallback_response(message: str, context: dict) -> dict:
    """Rule-based fallback when no LLM API key is configured."""
    user_lower = message.lower()

    if not is_llm_configured():
        setup_hint = (
            "\n\n---\n"
            "💡 **Enable full AI chat (like ChatGPT):**\n"
            "Add your API key to `backend/.env`:\n"
            "```\n"
            "LLM_PROVIDER=gemini\n"
            "GEMINI_API_KEY=your_key_here\n"
            "```\n"
            "Get a free key at: https://aistudio.google.com/apikey\n"
            "Then restart the backend server."
        )
    else:
        setup_hint = ""

    if any(kw in user_lower for kw in ['why', 'dangerous', 'explain', 'reason', 'spam', 'scam']):
        return {**_explain_danger(context), 'provider': 'fallback', 'setup_hint': not is_llm_configured()}

    if any(kw in user_lower for kw in ['what should', 'what to do', 'help', 'recommend', 'do now']):
        result = _what_to_do(context)
        result['reply'] += setup_hint
        return {**result, 'provider': 'fallback'}

    if any(kw in user_lower for kw in ['phishing', 'url', 'link', 'website']):
        result = _phishing_info(context)
        result['reply'] += setup_hint
        return {**result, 'provider': 'fallback'}

    if any(kw in user_lower for kw in ['fraud', 'fake', 'lottery', 'kyc', 'otp', 'bank']):
        result = _fraud_info(context)
        result['reply'] += setup_hint
        return {**result, 'provider': 'fallback'}

    # General conversational attempt without rigid templates
    reply = (
        f"You asked: \"{message}\"\n\n"
        "I'm the TextGuard SMS Security Assistant. I can help you with:\n"
        "• Understanding if an SMS is spam or a scam\n"
        "• Explaining phishing links and fraud patterns\n"
        "• What to do if you received a suspicious message\n"
        "• General mobile and SMS security tips\n\n"
        "Try analyzing an SMS first (SMS Detector page), then ask me about the results — "
        "or ask any cybersecurity question!"
    )
    reply += setup_hint
    return {'reply': reply, 'type': 'fallback', 'provider': 'fallback'}


def _explain_danger(context: dict) -> dict:
    prediction = context.get('prediction', 'unknown')
    reasons = context.get('reasons', [])
    confidence = context.get('confidence', 0)
    msg = context.get('message') or context.get('original_message', '')

    if prediction == 'spam':
        reply = (
            f"Based on analysis, this SMS is classified as **SPAM** ({confidence:.0%} confidence).\n\n"
        )
        if msg:
            reply += f"Message: \"{msg[:200]}\"\n\n"
        if reasons:
            reply += "Key reasons:\n" + '\n'.join(f"• {r}" for r in reasons[:6]) + "\n\n"
        reply += (
            "Scammers use urgency, fake rewards, and impersonation to trick people into "
            "clicking links or sharing OTPs. Never respond to unsolicited financial requests via SMS."
        )
    elif prediction == 'ham':
        reply = (
            f"This SMS appears **legitimate** ({confidence:.0%} confidence). "
            "However, always verify unexpected messages — especially those asking for money, OTP, or personal details."
        )
    else:
        reply = (
            "I don't have a specific SMS loaded. Go to SMS Detector, analyze a message, "
            "then come back here to ask me about it."
        )
    return {'reply': reply, 'type': 'explanation'}


def _what_to_do(context: dict) -> dict:
    prediction = context.get('prediction', 'ham')
    if prediction == 'spam':
        reply = (
            "**If you received a suspicious/spam SMS:**\n\n"
            "1. **Do NOT** click any links\n"
            "2. **Do NOT** share OTP, PIN, or bank details\n"
            "3. **Block** the sender immediately\n"
            "4. **Report** spam to TRAI by forwarding to 1909\n"
            "5. **Report** cyber fraud at cybercrime.gov.in or call **1930**\n"
            "6. If you already shared info, **contact your bank** immediately"
        )
    else:
        reply = (
            "**General SMS security tips:**\n\n"
            "• Never share OTP with anyone — banks never ask via SMS\n"
            "• Verify sender identity for financial messages\n"
            "• Use official banking apps, not SMS links\n"
            "• Enable spam filtering on your phone\n"
            "• Be skeptical of 'too good to be true' offers"
        )
    return {'reply': reply, 'type': 'recommendation'}


def _phishing_info(context: dict) -> dict:
    phishing = context.get('phishing_analysis', {})
    if phishing.get('analyses'):
        lines = ["**Phishing URL Analysis:**\n"]
        for a in phishing['analyses'][:3]:
            lines.append(f"• {a.get('domain', a.get('url'))}: **{a.get('status', 'unknown').upper()}** ({a.get('risk_percentage', 0)}% risk)")
            for factor in (a.get('risk_factors') or [])[:2]:
                lines.append(f"  - {factor}")
        lines.append(
            "\nPhishing sites mimic real banks/shops to steal login credentials. "
            "Always type official URLs manually or use the official app."
        )
        return {'reply': '\n'.join(lines), 'type': 'phishing'}

    return {
        'reply': (
            "No URLs were found in the analyzed SMS. If you have a suspicious link:\n"
            "• Don't click it\n• Check the domain carefully (e.g. paypa1.com vs paypal.com)\n"
            "• Use Google's Safe Browsing or VirusTotal to check URLs"
        ),
        'type': 'phishing',
    }


def _fraud_info(context: dict) -> dict:
    fraud_type = context.get('fraud_type') or 'Unknown scam'
    reply = (
        f"This message matches **{fraud_type}** patterns.\n\n"
        "Common Indian SMS fraud types:\n"
        "• **Banking/KYC fraud** — Fake account block, OTP requests\n"
        "• **Lottery scams** — 'You won ₹X lakh', claim prize\n"
        "• **Job scams** — Earn ₹5000/day, work from home\n"
        "• **Investment fraud** — Double your money, crypto schemes\n\n"
        "Legitimate organizations never ask for OTP or urgent payments via SMS."
    )
    return {'reply': reply, 'type': 'fraud'}
