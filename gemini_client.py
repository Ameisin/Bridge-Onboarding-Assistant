# gemini_client.py
import time
from google import genai
from typing import Any

from config import TEMPERATURE_JSON, TEMPERATURE_TEXTO
from gemini_config import obtener_config_gemini
from ollama_client import MetricasLlamada

_configured = False
client: genai.Client | None = None

def configurar_gemini() -> None:
    global _configured, client
    if _configured and client is not None:
        return

    config = obtener_config_gemini()
    client = genai.Client(api_key=config["api_key"])
    _configured = True

def llamar_gemini(
    prompt: str,
    model: str,
    temperatura: float,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    configurar_gemini()

    contenido = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"

    t0 = time.perf_counter()
    # El objeto response ahora se obtiene directamente a través del cliente
    response = client.models.generate_content(
        model=model,
        contents=contenido,
        config=genai.types.GenerateContentConfig(
            temperature=temperatura
        ),
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    # El SDK moderno usa un objeto de respuesta diferente para los metadatos
    usage = getattr(response, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
    total_tokens = getattr(usage, "total_token_count", None) if usage else None

    texto = response.text if response.text else ""

    metricas = MetricasLlamada(
        elapsed_ms=elapsed_ms,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )
    return texto, metricas

def llamar_gemini_json(
    prompt: str,
    model: str,
    temperatura: float,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    return llamar_gemini(
        prompt=prompt,
        model=model,
        temperatura=temperatura,
        system_prompt=system_prompt,
    )