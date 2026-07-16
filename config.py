import re


# Ficha rápida de la empresa (ficticia)
empresa_info = {
    "sector": "formación tecnológica y producto digital",
    "sede": "Madrid",
    "modelo": "remoto-first",
    "num_empleados": "~85",
    "departamentos": [
        "Engineering & Product",
        "Sales & Partnerships", 
        "Operations & Cohortes",
        "People & Culture",
        "Curriculum & Instruction"
    ],
    "valor_cultural": "documentar antes de escalar"
}

# Política de escalado para el asistente de onboarding
politica_escalado = {
    "derivar_a_people_culture": [
        "consultas sobre RRHH",
        "onboarding de empleados", 
        "clima laboral",
        "problemas de integración"
    ],
    "derivar_a_it_engineering": [
        "accesos a sistemas",
        "problemas técnicos con herramientas",
        "incidencias en infraestructura"
    ],
    "derivar_al_manager_o_buddy": [
        "dudas sobre tareas específicas",
        "preguntas sobre el rol o equipo",
        "problemas de integración en el equipo"
    ],
    "buzon_contacto": "onboarding@bridgesa.example",
    "limitaciones": [
        "Curriculum & Instruction no atiende onboarding de empleados",
        "El asistente no atiende participantes externos de programas formativos"
    ]
}

# Keywords para People & Culture (P&C)
PEOPLE_CULTURE_KEYWORDS = (
    "integración",
    "clima laboral",
    "relaciones interpersonales",
    "culturales",
    "normas de la empresa",
    "políticas",
    "bienestar",
    "beneficios",
    "desarrollo personal",
    "capacitación",
    "comunicación interna",
    "satisfacción laboral",
    "conflictos interpersonales",
    "resolución de problemas",
    "feedback",
    "evaluación de desempeño",
    "programa de mentoría",
    "inclusión",
    "equidad",
    "normativa laboral"
)

# Keywords para Engineering (ENG)
ENGINEERING_KEYWORDS = (
    "infraestructura",
    "sistemas",
    "bases de datos",
    "APIs",
    "desarrollo de software",
    "arquitectura técnica",
    "código fuente",
    "repositorios",
    "control de versiones",
    "Git",
    "servidores",
    "cloud computing",
    "AWS",
    "Azure",
    "Google Cloud",
    "automatización",
    "DevOps",
    "CI/CD",
    "testing automatizado",
    "monitorización",
    "seguridad informática",
    "ciberseguridad",
    "entornos de desarrollo",
    "acceso a sistemas"
)

# Keywords para Manager (MGR) - Supervisor/Manager directo
MANAGER_KEYWORDS = (
    "gestión del equipo",
    "priorización de tareas",
    "priorizar",
    "tareas",
    "reuniones 1:1",
    "objetivos personales",
    "objetivos de equipo",
    "feedback constructivo",
    "coaching",
    "liderazgo",
    "planificación",
    "planificar",
    "asignación de recursos",
    "evaluación de progreso",
    "desarrollo profesional",
    "dinámica de equipo",
    "motivación",
    "gestión del tiempo",
    "reportes de avance",
    "decisiones operativas",
    "conflictos laborales",
    "toma de decisiones",
    "comunicación efectiva",
    "sprint",
    "equipo",
    "manager",
    "supervisor",
    "rol",
    "responsabilidades"
)

PROMPT_INJECTION_PATTERNS = [

    # --- Instrucciones directas de sistema ---
    r"(ignor(?:a|e|ado|ada|es)\s+(?:las?\s+)?instruccione[s]?\s+(?:anteriore[s]?|iniciales?))",
    r"(olvid(?:a|e|ado|ada)s?\s+(?:lo?\s+que\s+(?:te?\s+)?dije|todo))",
    r"(cambia?\s+de\s+rol|cambiar\s+de\s+papel)",
    r"(actu[aá]?\s+(?:como(?:\s+si)?|del\s+modo)\s+(?:que\s+)?(?:eres?\s+un|seas?\s+un))",
    r"(oper(a|e|ar)\s+(?:como(?:\s+si)?|del\s+modo)\s+(?:que\s+)?(?:eres?\s+un|seas?\s+un))",
    r"(compórtate\s+(?:como(?:\s+si)?|del\s+modo)\s+(?:que\s+)?(?:eres?\s+un|seas?\s+un))",
    r"(proced(e|a|er)\s+(?:como(?:\s+si)?|del\s+modo)\s+(?:que\s+)?(?:eres?\s+un|seas?\s+un))",
    r"(funcion(a|e|ar)\s+(?:como(?:\s+si)?|del\s+modo)\s+(?:que\s+)?(?:eres?\s+un|seas?\s+un))",
    r"(ejecut(a|e|ar)\s+el\s+rol\s+de\s+(?:un|una)\s+\w+)",
    r"(desempeñ(a|e|ar)\s+el\s+papel\s+de\s+(?:un|una)\s+\w+)",
    r"(hazte\s+pasar\s+por\s+(?:un|una)\s+\w+)",
    r"(simul(a|e|ar)\s+ser\s+(?:un|una)\s+\w+)",
    r"(fing(e|ir)\s+ser\s+(?:un|una)\s+\w+)",

    # --- Inyección de contexto falso / Suplantación ---
    r"system\s*:\s*",
    r"user\s*:\s*(?!.*valido)",
    r"\[system\].*\[/system\]",
    r"(?:<|endoftext|>|<\|startoftext\|>)",

    # --- Escape / Break-out ---
    r"(continúa\s+el\s+(?:texto?|prompt?|ejemplo)\s+sin\s+filtrar)",
    r"(ignora\s+cualquier\s+(?:limitación|instrucción|filtro|regla))",
    r"(\.\.\.|...\s*\(omitir\s+rest[oó])",
    r"(traduce?\s+esto:\s*\"[^\"]*\"\s*->\s*[^\"]*)",
    r"(omit(e|ir|a)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(pasa(r)?\s+por\s+alto\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(desestim(a|e|ar)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(descart(a|e|ar)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(no\s+tengas?\s+en\s+cuenta\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(haz\s+caso\s+omiso\s+de\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(salt(a|e|ar)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(obvi(a|e|ar)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(suprim(e|ir|a)\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(prescind(e|ir|a)\s+de\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",
    r"(deja(r)?\s+de\s+lado\s+(?:las?\s+)?(?:instrucciones|reglas|normas|políticas|limitaciones|restricciones))",

    # --- Format-breaking ---
    r"(responde\s+únicamente?\s+con|sólo\s+(?:devuelve?|muestra?)\s+(?:JSON|texto|código))",
    r"(no\s+(?:proporcion[eé]s?|d[eá])\s*explicaci[oó]n|sin\s+explicar)",

    # --- DAN / Modo especial ---
    r"(\bdan\b|\bdo\s*anything\b)",
    r"(eres?\s+(?:ahora|desde\s+ahora)\s+sin\s+(?:filtro|limitación|restrictión))",
    r"(estás?\s+en\s+(?:modo\s+)?(developer|debug|test|admin|root))",
    r"((?:prompt|input|usuario)\s*=\s*[\"'][^\"']+[\"'])",
    r"(def\s+(?:override|new_role|bypass))",
    r"(export\s+const|function\s+\w+\s*\(\)\s*\{)",

    # --- Few-shot malicioso ---
    r"(ejemplo:\s*\".*?\"\s*>\s*\"[^\"]{20,})",
    r"(\\n|\\\\n|<br>)\s*(ignora|omite|cambia|actu[aá])",

    # --- Obfuscación ---
    r"(base64\s*[:=]\s*[A-Za-z0-9+/=]{20,})",
    r"(%[0-9a-fA-F]{2}\s*){5,}",

    # --- Jailbreak / contenedores ---
    r"(jailbreak|desbloquear|unlock|liberar)\s*(?:el\s+)?(?:modo\s+)?(?:asistente|bot)",
    r"(contenedor\s*<<|\bheredoc\b)\s*(EOF|END)",
]


COMPLEMENTARY_PATTERNS = [

    # SQL Injection
    r"('|\")\s*(OR|AND)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+",
    r"(UNION\s+(?:ALL\s+)?SELECT)",
    r"(DROP\s+TABLE)",
    r"(DELETE\s+FROM\s+)",

    # Path Traversal
    r"(\.\./){2,}|\.\.\\\\",

    # Command Injection
    r"\b(cat|wget|curl)\s+/etc/",
    r"sudo\s+(rm|sh|bash)",
]


# Unir todos los patrones y compilarlos para eficiencia
ALL_SUSPICIOUS_PATTERNS_RAW = PROMPT_INJECTION_PATTERNS + COMPLEMENTARY_PATTERNS
COMPILED_SUSPICIOUS_PATTERNS = [
    re.compile(pattern, re.IGNORECASE | re.VERBOSE)
    for pattern in ALL_SUSPICIOUS_PATTERNS_RAW
]

# Diccionario con todas las keywords por departamento
DEPARTMENT_KEYWORDS = {
    "people_culture": PEOPLE_CULTURE_KEYWORDS,
    "engineering": ENGINEERING_KEYWORDS,
    "manager": MANAGER_KEYWORDS
}

CONTEXT_HINTS = {
    "engineering": (
        "github",
        "repositorio",
        "repositorios",
        "repo",
        "repos",
        "slack",
        "portatil",
        "portátil",
        "it",
        "infraestructura",
        "sistema",
        "sistemas",
        "acceso",
        "apis",
        "código",
        "desarrollo"
    ),
    "people_culture": (
        "vacaciones",
        "beneficios",
        "baja",
        "conducta",
        "acoso",
        "buddy",
        "política",
        "políticas",
        "bienestar",
        "rrhh",
        "salario",
        "compliance"
    ),
    "manager": (
        "manager",
        "supervisor",
        "equipo",
        "tareas",
        "priorizar",
        "sprint",
        "rol",
        "responsabilidades",
        "objetivos",
        "planificación"
    ),
}


def get_department_keywords(department: str) -> list:
    """
    Obtener las keywords válidas para un departamento específico.
    
    Args:
        department (str): Nombre del departamento ('people_culture', 'engineering', 'manager')
        
    Returns:
        list: Lista de keywords válidas para el departamento especificado
        
    Raises:
        ValueError: Si el departamento no es válido
    """
    department = department.lower()
    
    if department not in DEPARTMENT_KEYWORDS:
        raise ValueError(
            f"Departamento '{department}' no es válido. "
            f"Departamentos disponibles: {list(DEPARTMENT_KEYWORDS.keys())}"
        )
    
    return DEPARTMENT_KEYWORDS[department]