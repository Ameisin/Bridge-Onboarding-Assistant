DAY_CONTEXT = {
    1: (
        "El empleado acaba de incorporarse. "
        "Prioriza accesos, herramientas, bienvenida y primeros pasos."
    ),
    2: (
        "El empleado ya tiene los accesos básicos. "
        "Prioriza formación y conocimiento del equipo."
    ),
    3: (
        "El empleado debe comenzar a trabajar en tareas reales. "
        "Evita repetir información del día 1."
    ),
    4: (
        "El empleado ya conoce las herramientas principales. "
        "Prioriza autonomía y buenas prácticas."
    ),
    5: (
        "El empleado está terminando su primera semana. "
        "Prioriza revisión del progreso y siguientes objetivos."
    ),
}


def build_chat_prompt(
    employee: dict,
    question: str,
    documents: list,
    onboarding_day: int,
    history: list | None = None,
) -> str:
    """
    Construye el prompt para el chat.
    """

    docs_text = ""

    for doc in documents:
        docs_text += (
            f"\nDocumento: {doc['id']}\n"
            f"Título: {doc['titulo']}\n"
            f"Contenido:\n{doc['cuerpo']}\n"
        )

    history_text = ""

    if history:
        for turn in history[-4:]:
            history_text += (
                f"{turn['role'].capitalize()}: {turn['content']}\n"
            )

    prompt = f"""
Eres el Employee Onboarding Assistant de Bridge SA.

Tu misión es ayudar únicamente con el onboarding de empleados.

REGLAS:

- Usa solamente la documentación proporcionada.
- Si la respuesta no aparece en la documentación, indícalo claramente.
- No inventes políticas.
- Responde de forma breve y profesional.
- Ten en cuenta el día de onboarding para adaptar la respuesta.

=========================
EMPLEADO
=========================

Nombre: {employee["nombre"]}
Departamento: {employee["departamento"]}
Perfil: {employee["perfil"]}
Modalidad: {employee["modalidad"]}

Día de onboarding: {onboarding_day}

Objetivo del día:
{DAY_CONTEXT.get(onboarding_day)}

=========================
DOCUMENTACIÓN
=========================

{docs_text}

=========================
HISTORIAL
=========================

{history_text}

=========================
PREGUNTA
=========================

{question}
"""

    return prompt.strip()


def build_checklist_prompt(
    employee: dict,
    onboarding_day: int,
    documents: list,
) -> str:
    """
    Construye el prompt para generar el checklist en JSON.
    """

    docs_text = ""

    for doc in documents:
        docs_text += (
            f"\nDocumento: {doc['id']}\n"
            f"Título: {doc['titulo']}\n"
            f"Contenido:\n{doc['cuerpo']}\n"
        )

    prompt = f"""
Eres el Employee Onboarding Assistant de Bridge SA.

Genera EXCLUSIVAMENTE un JSON válido.

No escribas texto antes ni después del JSON.

Utiliza únicamente la documentación proporcionada.

El checklist debe adaptarse al día de onboarding y evitar repetir tareas de días anteriores.

Objetivo del día:
{DAY_CONTEXT.get(onboarding_day)}

La estructura debe ser exactamente:

{{
  "empleado_id": "{employee["id"]}",
  "dia": {onboarding_day},
  "tareas": [
    {{
      "id": "t01",
      "titulo": "",
      "completada": false,
      "fuente_doc": ""
    }}
  ],
  "mensaje_resumen": ""
}}

=========================
EMPLEADO
=========================

Nombre: {employee["nombre"]}
Departamento: {employee["departamento"]}
Perfil: {employee["perfil"]}
Modalidad: {employee["modalidad"]}

=========================
DOCUMENTACIÓN
=========================

{docs_text}
"""

    return prompt.strip()