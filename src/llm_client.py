import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "No se encontró la variable GEMINI_API_KEY en el archivo .env"
            )

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # Cambia a 2.5-flash si tu proyecto tiene acceso
            contents=prompt,
        )

        return response.text

