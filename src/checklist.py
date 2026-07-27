from src.prompts import build_checklist_prompt
from src.context_selector import select_documents


class ChecklistAssistant:

    def __init__(self, llm, documents):
        self.llm = llm
        self.documents = documents

    def generate(
        self,
        employee,
        onboarding_day,
    ):

        docs = select_documents(
            self.documents,
            question=f"onboarding día {onboarding_day}",
            department=employee["departamento"],
        )

        prompt = build_checklist_prompt(
            employee=employee,
            onboarding_day=onboarding_day,
            documents=docs,
        )

        return self.llm.generate(prompt)