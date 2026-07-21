from src.context_selector import select_documents
from src.prompts import build_chat_prompt
from src.conversation_memory import ConversationMemory

class ChatAssistant:

    def __init__(self, llm, documents):
        self.llm = llm
        self.documents = documents
        self.memory = ConversationMemory()
    def chat(
        self,
        employee,
        question,
        onboarding_day,
    ):

        docs = select_documents(
            self.documents,
            question,
            employee["departamento"],
        )


        history = self.memory.get(employee["id"])

        prompt = build_chat_prompt(
            employee=employee,
            question=question,
            documents=docs,
            onboarding_day=onboarding_day,
            history=history,
        )

        answer = self.llm.generate(prompt)

        self.memory.add(
            employee["id"],
            "user",
            question,
        )

        self.memory.add(
            employee["id"],
            "assistant",
            answer,
        )

       
        # máximo 4 turnos
        self.history = self.history[-4:]

        return answer