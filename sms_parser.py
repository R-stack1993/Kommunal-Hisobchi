# sms_parser.py
"""
SMS parser for extracting utility meter readings from forwarded SMS messages.
Supports common Uzbek and Russian electricity/gas company SMS formats.
"""
import re


def parse_sms(text: str) -> dict:
    """
    Parse an SMS text to extract utility reading information.

    Returns a dict with keys:
        - 'reading': meter reading value (ko'rsatkich) or None
        - 'usage': consumption/sarf value or None
        - 'amount': payment amount (summa/to'lov) or None
        - 'utility_type': 'elektr' or 'gaz' or None if not determinable
    """
    result = {
        'reading': None,
        'usage': None,
        'amount': None,
        'utility_type': None,
    }

    if not text:
        return result

    # Normalize text: replace multiple spaces, strip
    normalized = re.sub(r'\s+', ' ', text.strip())

    # --- Extract reading value (ko'rsatkich / pokazanie) ---
    reading_patterns = [
        # Uzbek patterns
        r"[Jj]oriy\s+ko['\u2018\u2019]?rsatkich\s*[:=]?\s*([\d\s.,]+)",
        r"[Kk]o['\u2018\u2019]?rsatkich\s*[:=]?\s*([\d\s.,]+)",
        r"[Hh]isoblagich\s*[:=]?\s*([\d\s.,]+)",
        r"[Jj]oriy\s*[:=]?\s*([\d\s.,]+)\s*(?:kVt|kvt|m3|m\u00b3)",
        # Russian patterns
        r"[Пп]оказани[еяй]\s*[:=]?\s*([\d\s.,]+)",
        r"[Тт]екущ(?:ее|ий)\s+показани[еяй]\s*[:=]?\s*([\d\s.,]+)",
        r"[Сс]четчик\s*[:=]?\s*([\d\s.,]+)",
    ]

    for pattern in reading_patterns:
        match = re.search(pattern, normalized)
        if match:
            result['reading'] = _extract_number(match.group(1))
            break

    # --- Extract usage/consumption (sarf / raskhod) ---
    usage_patterns = [
        # Uzbek patterns
        r"[Ss]arf\s*[:=]?\s*([\d\s.,]+)\s*(?:kVt|kvt|m3|m\u00b3|kub)?",
        r"[Ss]arfiyat\s*[:=]?\s*([\d\s.,]+)",
        r"[Ii]steymol\s*[:=]?\s*([\d\s.,]+)",
        r"[Ff]oydalanish\s*[:=]?\s*([\d\s.,]+)",
        # Russian patterns
        r"[Рр]асход\s*[:=]?\s*([\d\s.,]+)\s*(?:кВт|квт|м3|м\u00b3|куб)?",
        r"[Пп]отреблени[ея]\s*[:=]?\s*([\d\s.,]+)",
    ]

    for pattern in usage_patterns:
        match = re.search(pattern, normalized)
        if match:
            result['usage'] = _extract_number(match.group(1))
            break

    # --- Extract amount/cost (summa / to'lov) ---
    amount_patterns = [
        # Uzbek patterns
        r"[Ss]umma\s*[:=]?\s*([\d\s.,]+)\s*(?:so['\u2018\u2019]?m|sum|UZS)?",
        r"[Tt]o['\u2018\u2019]?lov\s*[:=]?\s*([\d\s.,]+)\s*(?:so['\u2018\u2019]?m|sum|UZS)?",
        r"[Hh]isob\s*[:=]?\s*([\d\s.,]+)\s*(?:so['\u2018\u2019]?m|sum|UZS)?",
        r"[Jj]ami\s*[:=]?\s*([\d\s.,]+)\s*(?:so['\u2018\u2019]?m|sum|UZS)?",
        r"[Qq]arz\s*[:=]?\s*([\d\s.,]+)\s*(?:so['\u2018\u2019]?m|sum|UZS)?",
        # Russian patterns
        r"[Сс]умма\s*[:=]?\s*([\d\s.,]+)\s*(?:сум|сом|UZS)?",
        r"[Оо]плата\s*[:=]?\s*([\d\s.,]+)\s*(?:сум|сом|UZS)?",
        r"[Нн]ачислено\s*[:=]?\s*([\d\s.,]+)\s*(?:сум|сом|UZS)?",
        r"[Ии]того\s*[:=]?\s*([\d\s.,]+)\s*(?:сум|сом|UZS)?",
        r"[Дд]олг\s*[:=]?\s*([\d\s.,]+)\s*(?:сум|сом|UZS)?",
    ]

    for pattern in amount_patterns:
        match = re.search(pattern, normalized)
        if match:
            result['amount'] = _extract_number(match.group(1))
            break

    # --- Detect utility type ---
    elektr_keywords = [
        r'\b(?:elektr|electr)\b', r'\bkVt\b', r'\bkvt\b', r'\bkWh\b',
        r'\b(?:tok|energiya)\b',
        r'\b(?:электр|кВт|кВтч|энерги)\b',
    ]
    gaz_keywords = [
        r'\b(?:gaz|gas)\b', r'\bm3\b', r'\bm\u00b3\b', r'\bkub\b',
        r'\btabiiy\s+gaz\b',
        r'\b(?:газ|м3|м\u00b3|куб)\b',
    ]

    elektr_score = sum(1 for p in elektr_keywords if re.search(p, normalized, re.IGNORECASE))
    gaz_score = sum(1 for p in gaz_keywords if re.search(p, normalized, re.IGNORECASE))

    if elektr_score > gaz_score:
        result['utility_type'] = 'elektr'
    elif gaz_score > elektr_score:
        result['utility_type'] = 'gaz'

    return result


def _extract_number(raw: str) -> float:
    """
    Clean a raw numeric string and convert to float.
    Handles spaces as thousand separators, commas, etc.
    """
    # Remove spaces (thousand separators)
    cleaned = raw.replace(' ', '').replace('\u00a0', '')
    # Replace comma with dot for decimal
    # If there are both commas and dots, assume last separator is decimal
    if ',' in cleaned and '.' in cleaned:
        # e.g., "1.234,56" -> "1234.56"
        cleaned = cleaned.replace('.', '').replace(',', '.')
    elif ',' in cleaned:
        # Could be decimal comma or thousand separator
        parts = cleaned.split(',')
        if len(parts[-1]) == 3 and len(parts) > 1:
            # Thousand separator: "150,000" -> "150000"
            cleaned = cleaned.replace(',', '')
        else:
            # Decimal: "123,45" -> "123.45"
            cleaned = cleaned.replace(',', '.')

    try:
        return float(cleaned)
    except ValueError:
        # Try extracting just digits
        digits = re.sub(r'[^\d.]', '', cleaned)
        if digits:
            return float(digits)
        return 0.0


def is_sms_like(text: str) -> bool:
    """
    Check if a text message looks like a forwarded SMS from a utility company.
    """
    if not text:
        return False

    # Keywords that suggest utility SMS
    sms_indicators = [
        r"ko['\u2018\u2019]?rsatkich",
        r"[Ss]arf",
        r"[Ss]umma",
        r"[Tt]o['\u2018\u2019]?lov",
        r"[Hh]isob",
        r"kVt|kvt|kWh",
        r"m3|m\u00b3",
        r"[Пп]оказани",
        r"[Рр]асход",
        r"[Сс]умма",
        r"[Оо]плата",
        r"[Сс]четчик",
        r"кВт|м3|м\u00b3",
        r"elektr|gaz|газ|электр",
    ]

    matches = sum(1 for p in sms_indicators if re.search(p, text, re.IGNORECASE))
    return matches >= 2
