"""Multilingual SMS language detection and translation."""

import re

from langdetect import DetectorFactory, detect

DetectorFactory.seed = 42

LANGUAGE_MAP = {
    'en': 'english',
    'hi': 'hindi',
    'mr': 'marathi',
}

DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')


def detect_language(text: str) -> str:
    """Detect language: English, Hindi, or Marathi."""
    if not text or not text.strip():
        return 'en'

    if DEVANAGARI_PATTERN.search(text):
        try:
            lang = detect(text)
            if lang in ('hi', 'mr'):
                return lang
            return 'hi'
        except Exception:
            return 'hi'

    try:
        lang = detect(text)
        return lang if lang in LANGUAGE_MAP else 'en'
    except Exception:
        return 'en'


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate non-English SMS to English for ML prediction."""
    if source_lang == 'en':
        return text

    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source=source_lang, target='en')
        return translator.translate(text)
    except Exception:
        return text


def get_language_name(code: str) -> str:
    return LANGUAGE_MAP.get(code, 'english')
