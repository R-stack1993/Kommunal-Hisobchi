# locales/__init__.py
from locales.uz import MESSAGES as UZ_MESSAGES
from locales.ru import MESSAGES as RU_MESSAGES

_LANG_MAP = {
    'uz': UZ_MESSAGES,
    'ru': RU_MESSAGES,
}


def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """Fetch a localized string by key and language, formatting with kwargs if provided."""
    messages = _LANG_MAP.get(lang, UZ_MESSAGES)
    text = messages.get(key, UZ_MESSAGES.get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
