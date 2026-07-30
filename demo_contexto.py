from context import (
    DATA_DIR,
    read_empresa,
    read_faq,
    read_docs,
    read_empleados,
    select_faq,
    select_docs,
)
from config import INFO_EMPRESA

# from validators import validacion_input
# validacion = validacion_input("¿Cómo accedo a GitHub?")
# print(f"Validación de entrada: {validacion}")


def demo_contexto(query: str, max_faq: int = 3, max_docs: int = 3) -> dict:
    data_dir = DATA_DIR

    faq_path = data_dir / "faq_onboarding.json"
    docs_path = data_dir / "onboarding_docs.json"
    empleados_path = data_dir / "empleados_demo.json"
    empresa_path = data_dir / "empresa.json"

    faq = read_faq(faq_path) if faq_path.exists() else []
    docs = read_docs(docs_path) if docs_path.exists() else []
    empleados = read_empleados(empleados_path) if empleados_path.exists() else []
    empresa = read_empresa(empresa_path) if empresa_path.exists() else INFO_EMPRESA

    faq_matches = select_faq(faq, query, max_results=max_faq)
    docs_matches = select_docs(docs, query, max_results=max_docs)

    return {
        "query": query,
        "empresa": empresa,
        "empleados": empleados[:3],
        "faq": faq_matches,
        "docs": docs_matches,
    }


def imprimir_contexto(contexto: dict) -> None:
    print("=== Demo de obtención de contexto ===")
    print(f"Consulta: {contexto['query']}")
    print()

    print("Empresa:")
    print(contexto["empresa"] or {"mensaje": "No hay datos de empresa disponibles"})
    print()

    print("FAQs relevantes:")
    if contexto["faq"]:
        for entry in contexto["faq"]:
            print(f"- {entry.get('pregunta', 'Sin pregunta')}")
            if entry.get("respuesta"):
                print(f"  {entry['respuesta']}")
    else:
        print("- No se encontraron FAQs relevantes")
    print()

    print("Documentos relevantes:")
    if contexto["docs"]:
        for entry in contexto["docs"]:
            print(f"- {entry.get('titulo', 'Sin título')}")
            if entry.get("cuerpo"):
                print(f"  {entry['cuerpo']}")
    else:
        print("- No se encontraron documentos relevantes")
    print()

    print("Empleados de ejemplo:")
    if contexto["empleados"]:
        for empleado in contexto["empleados"]:
            print(f"- {empleado.get('nombre', 'Sin nombre')} ({empleado.get('rol', 'Sin rol')})")
    else:
        print("- No hay empleados de ejemplo disponibles")


if __name__ == "__main__":
    query = "repositorio github"
    contexto = demo_contexto(query)
    imprimir_contexto(contexto)