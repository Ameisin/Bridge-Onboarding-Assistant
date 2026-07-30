# main.py
from __future__ import annotations
import os
import argparse

from src.context_selector import load_documents
from src.employee_service import load_employees, get_employee
from src.llm_client import LLMClient
from src.chat import ChatAssistant
from src.checklist import ChecklistAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bench",
        action="store_true",
        help="Ejecutar el benchmark de modelos",
    )
    parser.set_defaults(mode="manual")
    return parser


def resolve_mode(args: argparse.Namespace) -> str:
    if args.bench:
        return "bench"
    return "manual"


def run_benchmark() -> None:
    from benchmark import BenchmarkLauncher

    try:
        BenchmarkLauncher().launch()
    except ImportError as exc:
        print(f"Error al ejecutar el benchmark: {exc}")
        print("El benchmark no está instalado o configurado correctamente.")


def run_demos() -> None:
    documents = load_documents("data/onboarding_docs.json")
    employees = load_employees("data/empleados_demo.json")

    llm = LLMClient()

    chat = ChatAssistant(llm, documents)
    checklist = ChecklistAssistant(llm, documents)

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

    print("\n")
    print("=" * 80)
    print("DEMO 2 - CHECKLIST")
    print("=" * 80)

    checklist_json = checklist.generate(
        employee=employee,
        onboarding_day=1,
    )
    print(checklist_json)

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


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    parser = build_parser()
    args = parser.parse_args()
    mode = resolve_mode(args)

    if mode == "bench":
        run_benchmark()
        return

    run_demos()


if __name__ == "__main__":
    main()