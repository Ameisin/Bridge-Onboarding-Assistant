from pathlib import Path

import config
import context
import validators

DATA_DIR = Path(__file__).parent / "data"


def infer_profile(query: str) -> str:
    """Intenta inferir un perfil desde palabras clave del usuario."""
    normalized = (query or "").lower()
    if any(token in normalized for token in ("ventas", "cliente", "comercial", "pipeline")):
        return "comercial"
    if any(token in normalized for token in ("python", "api", "github", "repositorio", "desarrollo", "código")):
        return "dev_junior"
    if any(token in normalized for token in ("arquitectura", "microservicios", "cloud", "devops", "infraestructura")):
        return "dev_senior"
    if any(token in normalized for token in ("europa", "remote", "horario", "timezone")):
        return "remoto_eu"
    return "dev_junior"


def build_llm_payload(query: str, derivation: dict[str, object], context_items: list[dict], profile_key: str | None = None) -> dict[str, object]:
    """Construye el payload que se enviará al LLM usando el sistema y el perfil configurados."""
    profile_key = profile_key or infer_profile(query)
    profile_role = config.PERFILES.get(profile_key, config.PERFILES["dev_junior"])["rol"]

    context_text = "\n".join(
        f"- {item.get('titulo', 'Documento')}: {item.get('cuerpo', '')}" for item in context_items
    )
    user_prompt = (
        f"Consulta del usuario: {query}\n"
        f"Departamento derivado: {derivation.get('department_label', derivation.get('department'))}\n"
        f"Contexto relevante:\n{context_text or 'Sin contexto adicional.'}"
    )

    return {
        "system_prompt": config.SYSTEM_PROMPT,
        "profile_role": profile_role,
        "user_prompt": user_prompt,
    }


def answer_query(query: str) -> dict[str, object]:
    """
    Deriva el prompt a un departamento y recupera la mejor respuesta desde FAQ o documentos.
    """
    derivation = validators.derive_department(query)
    if not derivation["is_valid"]:
        return {
            "is_valid": False,
            "department": None,
            "answer": "No puedo ayudar con esa consulta porque está fuera del contexto válido del onboarding.",
        }

    faq_entries = context.read_faq(DATA_DIR / "faq_onboarding.json")
    docs_entries = context.read_docs(DATA_DIR / "onboarding_docs.json")

    doc_matches = context.select_docs(docs_entries, query, max_results=3)
    if doc_matches:
        best_doc = doc_matches[0]
        payload = build_llm_payload(query, derivation, doc_matches)
        return {
            "is_valid": True,
            "department": derivation["department"],
            "answer": best_doc.get("cuerpo", "No tengo documentación para esa consulta."),
            "source": "doc",
            "doc_id": best_doc.get("id"),
            "llm_payload": payload,
        }

    faq_matches = context.select_faq(faq_entries, query, max_results=3)
    if faq_matches:
        best_faq = faq_matches[0]
        payload = build_llm_payload(query, derivation, faq_matches)
        return {
            "is_valid": True,
            "department": derivation["department"],
            "answer": best_faq.get("respuesta_corta", "No tengo una respuesta documentada para esa consulta."),
            "source": "faq",
            "faq_id": best_faq.get("id"),
            "llm_payload": payload,
        }

    payload = build_llm_payload(query, derivation, [])
    return {
        "is_valid": True,
        "department": derivation["department"],
        "answer": "No tengo una respuesta documentada para esa consulta, pero puedo derivarla a un canal humano.",
        "source": "fallback",
        "llm_payload": payload,
    }


if __name__ == "__main__":
    print("Asistente de onboarding de Bridge SA")
    print("Escribe tus preguntas sobre onboarding. Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tu consulta: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("Hasta pronto.")
            break

        result = answer_query(user_input)
        if result["is_valid"]:
            print(f"\nDepartamento: {result['department']}")
            print(f"Fuente: {result['source']}")
            print("Respuesta:")
            print(result["answer"])
        else:
            print("Respuesta:")
            print(result["answer"])

        print("\n" + "-" * 50 + "\n")
