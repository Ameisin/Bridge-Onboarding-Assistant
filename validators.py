import re

import config as conf

DEPARTMENT_LABELS = {
    "people_culture": "People & Culture",
    "engineering": "Engineering",
    "manager": "Manager",
}


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


def _normalize_phrase(phrase: str) -> str:
    return re.sub(r"\s+", " ", phrase.strip()).casefold()


def derive_department(phrase: str) -> dict[str, object]:
    """
    Deriva un prompt a un departamento si encaja con el contexto de onboarding.
    Si el prompt es sospechoso o no contiene palabras clave válidas, se rechaza.
    """
    if not isinstance(phrase, str) or not phrase.strip():
        return {"is_valid": False, "department": None, "department_label": None, "suspicious": None, "matches": []}

    suspicious = has_suspicious_patterns(phrase)
    if suspicious["is_malicious"]:
        return {"is_valid": False, "department": None, "department_label": None, "suspicious": suspicious, "matches": []}

    normalized_phrase = _normalize_phrase(phrase)

    for department, hints in conf.CONTEXT_HINTS.items():
        if any(hint in normalized_phrase for hint in hints):
            return {
                "is_valid": True,
                "department": department,
                "department_label": DEPARTMENT_LABELS[department],
                "suspicious": None,
                "matches": list(hints),
            }

    best_department: str | None = None
    best_matches: list[str] = []

    for department in conf.DEPARTMENT_KEYWORDS:
        matches = []
        for keyword in conf.get_department_keywords(department):
            pattern = re.compile(rf"(?<!\w){re.escape(keyword.casefold())}(?!\w)")
            if pattern.search(normalized_phrase):
                matches.append(keyword.casefold())

        if matches and (
            best_department is None
            or len(matches) > len(best_matches)
            or (len(matches) == len(best_matches) and department < best_department)
        ):
            best_department = department
            best_matches = matches

    if best_department is None:
        return {"is_valid": False, "department": None, "department_label": None, "suspicious": None, "matches": []}

    return {
        "is_valid": True,
        "department": best_department,
        "department_label": DEPARTMENT_LABELS[best_department],
        "suspicious": None,
        "matches": best_matches,
    }


def is_valid_prompt(phrase: str, department: str) -> dict[str, object]:
    """
    Verificar si una frase es válida para un departamento.
    """
    if not isinstance(phrase, str) or not phrase.strip():
        return {"is_valid": False, "suspicious": None}

    if not isinstance(department, str) or not department.strip():
        return {"is_valid": False, "suspicious": None}

    normalized_department = department.strip().casefold()
    if normalized_department not in DEPARTMENT_LABELS:
        return {"is_valid": False, "suspicious": None}

    derivation = derive_department(phrase)
    if not derivation["is_valid"]:
        return {"is_valid": False, "suspicious": derivation.get("suspicious")}

    if derivation["department"] != normalized_department:
        return {"is_valid": False, "suspicious": derivation.get("suspicious")}

    return {
        "is_valid": True,
        "suspicious": None,
        "department": derivation["department"],
        "department_label": derivation["department_label"],
    }