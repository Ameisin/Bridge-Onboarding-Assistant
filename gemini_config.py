import os
from dotenv import load_dotenv

_configured = False

def configurar_gemini_auth() -> None:
    global _configured
    if _configured:
        return

    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")

    _configured = True

def obtener_config_gemini() -> dict[str, str]:
    configurar_gemini_auth()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY está vacía o no definida")

    return {"api_key": api_key}