import re

import config as conf

def has_suspicious_patterns(keyword: str) -> dict[str, object]:
    """
    Detecta si un prompt contiene patrones maliciosos.
    Devuelve un diccionario con:
      - is_malicious: bool
      - matches: lista de patrones que hicieron match
    """
    if not isinstance(keyword, str) or not keyword.strip():
        return {
            "is_malicious": False,
            "matches": []
        }

    normalized = keyword.strip().casefold()

    matches = []
    for pattern in conf.COMPILED_SUSPICIOUS_PATTERNS:
        if pattern.search(normalized):
            matches.append(pattern.pattern)

    return {
        "is_malicious": bool(matches),
        "matches": matches
    }


def is_valid_prompt(phrase: str, department: str) -> dict[str, object]:
    """
    Verificar si una frase es válida para un departamento.
    """
    if not isinstance(phrase, str) or not phrase.strip():
        return {"is_valid": False, "suspicious": None}

    suspicious = has_suspicious_patterns(phrase)
    if suspicious["is_malicious"]:
        return {"is_valid": False, "suspicious": suspicious}

    normalized_phrase = re.sub(r"\s+", " ", phrase.strip()).casefold()
    valid_keywords = {kw.casefold() for kw in conf.get_department_keywords(department)}

    for keyword in valid_keywords:
        pattern = re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)")
        if pattern.search(normalized_phrase):
            return {"is_valid": True, "suspicious": None}

    return {"is_valid": False, "suspicious": None}