import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Modelo recomendado por el benchmark (ver entregables/recomendacion.md)
MODELO_ASISTENTE = "gemini-3.5-flash-lite"
TEMPERATURA_ASISTENTE = 0.2


class LLMClient:

    def __init__(self, model: str = MODELO_ASISTENTE, temperature: float = TEMPERATURA_ASISTENTE):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Falta GEMINI_API_KEY en el archivo .env (copia .env.example a .env y añade tu clave)."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=self.temperature),
        )

        return response.text
