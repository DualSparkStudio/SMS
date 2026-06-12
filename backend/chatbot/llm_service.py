"""LLM integration for conversational AI assistant (Gemini / OpenAI)."""

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are TextGuard AI Security Assistant — an expert cybersecurity advisor specializing in SMS spam detection, phishing, fraud prevention, and mobile security in India.

Your role:
- Answer ANY user question naturally and conversationally, like ChatGPT or Gemini
- Explain why SMS messages are dangerous, how scams work, and what users should do
- Provide clear, practical security advice tailored for Indian users
- Use simple language; explain technical terms when needed
- Reference TRAI DND (1909), National Cyber Crime Helpline (1930), and official bank practices when relevant

Rules:
- NEVER ask users to share OTPs, PINs, or passwords
- NEVER tell users to click suspicious links
- If SMS analysis context is provided below, use it for specific, accurate answers about that message
- For off-topic questions, answer briefly then offer to help with SMS/cybersecurity
- Use bullet points and short paragraphs for readability
- Be empathetic if the user may have been scammed

"""


def _build_system_message(context: dict | None) -> str:
    prompt = SYSTEM_PROMPT
    if not context:
        return prompt + "\nNo specific SMS is loaded. Answer general SMS security questions."

    parts = ["\n--- SMS Analysis Context ---"]
    if context.get('original_message') or context.get('message'):
        parts.append(f"Message: {context.get('original_message') or context.get('message')}")
    if context.get('prediction'):
        parts.append(f"Classification: {context['prediction'].upper()} ({context.get('confidence', 0):.0%} confidence)")
    if context.get('fraud_type'):
        parts.append(f"Fraud Type: {context['fraud_type']}")
    if context.get('security_score') is not None:
        parts.append(f"Security Score: {context['security_score']}/100")
    if context.get('reasons'):
        parts.append("Reasons: " + "; ".join(context['reasons']))
    if context.get('suspicious_words'):
        parts.append("Suspicious words: " + ", ".join(context['suspicious_words']))
    if context.get('phishing_analysis', {}).get('analyses'):
        for a in context['phishing_analysis']['analyses'][:3]:
            parts.append(f"URL {a.get('url')}: {a.get('status')} ({a.get('risk_percentage')}% risk)")
    if context.get('xai_summary'):
        parts.append(f"AI Summary: {context['xai_summary']}")
    parts.append("--- End Context ---\n")
    return prompt + "\n".join(parts)


def _normalize_history(history: list) -> list[dict]:
    """Convert frontend history to provider message format."""
    messages = []
    for item in history[-20:]:
        role = item.get('role', 'user')
        content = (item.get('content') or item.get('text') or '').strip()
        if not content:
            continue
        if role in ('user', 'assistant'):
            messages.append({'role': role, 'content': content})
    return messages


def chat_with_llm(user_message: str, history: list | None = None, context: dict | None = None) -> dict:
    """
    Generate a conversational response using configured LLM provider.
    Returns dict with reply, type, provider.
    """
    provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
    history = _normalize_history(history or [])
    system_message = _build_system_message(context)

    if provider == 'openai':
        result = _chat_openai(user_message, history, system_message)
        if result:
            return result

    if provider in ('gemini', 'google'):
        result = _chat_gemini(user_message, history, system_message)
        if result:
            return result

    # Auto-fallback: try whichever API key is available
    if os.getenv('OPENAI_API_KEY'):
        result = _chat_openai(user_message, history, system_message)
        if result:
            return result

    if os.getenv('GEMINI_API_KEY'):
        result = _chat_gemini(user_message, history, system_message)
        if result:
            return result

    return None


def _chat_openai(user_message: str, history: list, system_message: str) -> dict | None:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        messages = [{'role': 'system', 'content': system_message}]
        messages.extend(history)
        messages.append({'role': 'user', 'content': user_message})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content.strip()
        return {'reply': reply, 'type': 'llm', 'provider': 'openai', 'model': model}
    except Exception as e:
        logger.error('OpenAI chat failed: %s', e)
        return None


def _chat_gemini(user_message: str, history: list, system_message: str) -> dict | None:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    primary = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    fallback_models = [
        primary,
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash-lite',
    ]
    # Deduplicate while preserving order
    models_to_try = list(dict.fromkeys(fallback_models))

    gemini_history = []
    for msg in history:
        role = 'user' if msg['role'] == 'user' else 'model'
        gemini_history.append({'role': role, 'parts': [msg['content']]})

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system_message,
            )
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(user_message)
            reply = response.text.strip()
            return {'reply': reply, 'type': 'llm', 'provider': 'gemini', 'model': model_name}
        except Exception as e:
            last_error = e
            logger.warning('Gemini model %s failed: %s', model_name, e)
            continue

    logger.error('All Gemini models failed. Last error: %s', last_error)
    return None


def is_llm_configured() -> bool:
    return bool(os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY'))


SMS_CLASSIFICATION_PROMPT = """You are TextGuard's SMS security classifier for India. Classify the message as spam or ham (legitimate).

Respond with ONLY a single JSON object (no markdown, no code fences):
{{
  "prediction": "spam" or "ham",
  "confidence": <float between 0.0 and 1.0>,
  "fraud_type": "<Banking Fraud|Lottery Scam|Phishing|Wallet Scam|Fake Job Scam|Investment Scam|null>",
  "reasons": ["<reason1>", "<reason2>"],
  "explanation": "<one sentence summary>"
}}

Spam indicators include: shortened URLs (bit.ly, tinyurl), fake wallet/transfer/payment notifications, urgency, impersonation of banks or delivery apps, poor grammar or missing spaces, unsolicited money claims, "check now" with links, fake helplines, random account numbers with lure amounts.

Ham examples: personal conversation, legitimate appointment reminders without suspicious links, normal OTP texts without phishing URLs.

SMS to analyze:
\"\"\"{message}\"\"\"
"""


def _parse_classification_json(text: str) -> dict | None:
    """Extract and validate classification JSON from LLM output."""
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

    prediction = str(data.get('prediction', '')).lower().strip()
    if prediction not in ('spam', 'ham'):
        return None

    try:
        confidence = float(data.get('confidence', 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    fraud_type = data.get('fraud_type')
    if fraud_type in (None, 'null', ''):
        fraud_type = None

    reasons = data.get('reasons') or []
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    return {
        'prediction': prediction,
        'confidence': round(confidence, 4),
        'fraud_type': fraud_type,
        'reasons': [str(r) for r in reasons if r][:6],
        'explanation': str(data.get('explanation', '')).strip(),
    }


def _classify_openai(message: str) -> dict | None:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        prompt = SMS_CLASSIFICATION_PROMPT.format(message=message[:4000])

        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1,
            max_tokens=512,
        )
        parsed = _parse_classification_json(response.choices[0].message.content.strip())
        if parsed:
            parsed['provider'] = 'openai'
            parsed['model'] = model
        return parsed
    except Exception as e:
        logger.error('OpenAI SMS classification failed: %s', e)
        return None


def _classify_gemini(message: str) -> dict | None:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    classify_model = os.getenv('GEMINI_CLASSIFY_MODEL', 'gemini-2.5-flash-lite')
    models_to_try = list(dict.fromkeys([classify_model, 'gemini-2.5-flash-lite']))[:2]
    prompt = SMS_CLASSIFICATION_PROMPT.format(message=message[:4000])

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                ),
            )
            parsed = _parse_classification_json(response.text.strip())
            if parsed:
                parsed['provider'] = 'gemini'
                parsed['model'] = model_name
                return parsed
        except Exception as e:
            last_error = e
            logger.warning('Gemini classification model %s failed: %s', model_name, e)

    logger.error('All Gemini classification models failed. Last error: %s', last_error)
    return None


def _classify_sms_inner(message: str) -> dict | None:
    provider = os.getenv('LLM_PROVIDER', 'gemini').lower()

    if provider == 'openai' and os.getenv('OPENAI_API_KEY'):
        return _classify_openai(message)

    if provider in ('gemini', 'google') and os.getenv('GEMINI_API_KEY'):
        return _classify_gemini(message)

    if os.getenv('GEMINI_API_KEY'):
        return _classify_gemini(message)

    if os.getenv('OPENAI_API_KEY'):
        return _classify_openai(message)

    return None


def classify_sms_with_llm(message: str, timeout: int = 8) -> dict | None:
    """Classify SMS as spam/ham using the configured LLM. Returns None if unavailable."""
    if not is_llm_configured():
        return None

    try:
        timeout_secs = int(os.getenv('LLM_CLASSIFY_TIMEOUT', timeout))
    except (TypeError, ValueError):
        timeout_secs = timeout

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(_classify_sms_inner, message)
    try:
        return future.result(timeout=timeout_secs)
    except FuturesTimeout:
        logger.warning('SMS AI classification timed out after %ss', timeout_secs)
        return None
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
