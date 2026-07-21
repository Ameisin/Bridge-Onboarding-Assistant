from src.context_selector import load_documents
from src.employee_service import load_employees, get_employee
from src.llm_client import LLMClient

from src.chat import ChatAssistant
from src.checklist import ChecklistAssistant

from dotenv import load_dotenv
import os

def main():

    # Cargar datos
    documents = load_documents("data/onboarding_docs.json")
    employees = load_employees("data/empleados_demo.json")

    # Crear cliente LLMp
    llm = LLMClient()
    # Crear asistentes
    chat = ChatAssistant(llm, documents)
    checklist = ChecklistAssistant(llm, documents)

    # ==================================================
    # DEMO 1
    # Conversación (Dev Junior)
    # ==================================================

    print("=" * 80)
    print("DEMO 1 - CHAT")
    print("=" * 80)

    employee = get_employee("emp_01", employees)

    answer = chat.chat(
        employee=employee,
        question="¿Cómo consigo acceso a GitHub?",
        onboarding_day=1,
    )

    print(answer)

    # ==================================================
    # DEMO 2
    # Checklist JSON
    # ==================================================

    print("\n")
    print("=" * 80)
    print("DEMO 2 - CHECKLIST")
    print("=" * 80)

    checklist_json = checklist.generate(
        employee=employee,
        onboarding_day=1,
    )

    print(checklist_json)

    # ==================================================
    # DEMO 3
    # Comparación de perfiles
    # ==================================================

    print("\n")
    print("=" * 80)
    print("DEMO 3 - COMPARACIÓN DE PERFILES")
    print("=" * 80)

    commercial = get_employee("emp_02", employees)
    remote = get_employee("emp_03", employees)

    question = "¿Cómo funciona la política de trabajo remoto?"

    print("\n--- Comercial ---\n")

    print(
        chat.chat(
            employee=commercial,
            question=question,
            onboarding_day=2,
        )
    )

    print("\n--- Remoto UE ---\n")

    print(
        chat.chat(
            employee=remote,
            question=question,
            onboarding_day=2,
        )
    )
load_dotenv()

print(os.getenv("GEMINI_API_KEY"))


if __name__ == "__main__":
    main()