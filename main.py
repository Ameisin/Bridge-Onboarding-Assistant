from pathlib import Path

import context
import validators

DATA_DIR = Path(__file__).parent / "data"


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
        return {
            "is_valid": True,
            "department": derivation["department"],
            "answer": best_doc.get("cuerpo", "No tengo documentación para esa consulta."),
            "source": "doc",
            "doc_id": best_doc.get("id"),
        }

    faq_matches = context.select_faq(faq_entries, query, max_results=3)
    if faq_matches:
        best_faq = faq_matches[0]
        return {
            "is_valid": True,
            "department": derivation["department"],
            "answer": best_faq.get("respuesta_corta", "No tengo una respuesta documentada para esa consulta."),
            "source": "faq",
            "faq_id": best_faq.get("id"),
        }

    return {
        "is_valid": True,
        "department": derivation["department"],
        "answer": "No tengo una respuesta documentada para esa consulta, pero puedo derivarla a un canal humano.",
        "source": "fallback",
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
