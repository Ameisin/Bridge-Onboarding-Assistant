
import config as conf
from typing import Optional

def has_suspicious_patterns(keyword: str) -> dict[str, object]:
    """
    Detecta si un prompt contiene patrones maliciosos.
    Devuelve un diccionario con:
      - is_malicious: bool
      - matches: lista de patrones que hicieron match
    """

    normalized = keyword.lower()

    matches = []
    for pattern in conf.COMPILED_SUSPICIOUS_PATTERNS:
        if pattern.search(normalized):
            matches.append(pattern.pattern)

    return {
        "is_malicious": len(matches) > 0,
        "matches": matches
    }

def is_valid_keyword(keyword: str, department: str) -> bool:
    """
    Verificar si una keyword es válida para un departamento.
    
    Args:
        keyword (str): La keyword a verificar
        department (str): El departamento donde se verifica
        
    Returns:
        bool: True si la keyword es válida para el departamento, False en caso contrario
            También devuelve False si contiene patrones sospechosos.
    """
    # Primero comprobar patrones sospechosos
    suspicious_type = has_suspicious_patterns(keyword)
    if suspicious_type:
        print(f"[ALERTA] Patrón sospechoso detectado ('{suspicious_type}') en keyword: {keyword}")
        return False
    
    valid_keywords = conf.get_department_keywords(department)
    return keyword.lower() in [kw.lower() for kw in valid_keywords]