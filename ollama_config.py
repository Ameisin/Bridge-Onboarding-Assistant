# ollama_config.py
import os
from dotenv import load_dotenv

_configured = False

def configurar_ollama_token() -> None:
    global _configured

    if _configured:
        return

    load_dotenv()

    if not os.getenv("OLLAMA_HOST"):
        raise RuntimeError("Falta OLLAMA_HOST en el archivo .env")

    _configured = True


def obtener_config_ollama() -> tuple[str, dict]:
    configurar_ollama_token()

    host = os.getenv("OLLAMA_HOST", "").strip()
    token = os.getenv("OLLAMA_TOKEN", "").strip()

    if not host:
        raise RuntimeError("OLLAMA_HOST está vacío o no definido")

    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return host, headers