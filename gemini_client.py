# gemini_client.py
import time

from google.genai import types
from config import TEMPERATURE_JSON, TEMPERATURE_TEXTO
from gemini_config import obtener_config_gemini
from ollama_client_old import MetricasLlamada

_configured = False

def configurar_gemini() -> None:
    global _configured
    if _configured:
        return

    config = obtener_config_gemini()
    configure(api_key=config["api_key"])
    _configured = True

def llamar_gemini(
    prompt: str,
    model: str,
    temperatura: float=TEMPERATURE_TEXTO,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    configurar_gemini()

    modelo = model
    contenido = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"

    t0 = time.perf_counter()
    response = client.models.generate_content(
        modelo,
        contenido,
        config={"temperature": temperatura}
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    usage = getattr(response, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
    total_tokens = getattr(usage, "total_token_count", None) if usage else None

    texto = getattr(response, "text", "") or ""

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
    temperatura: float=TEMPERATURE_JSON,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    return llamar_gemini(
        prompt=prompt,
        model=model,
        temperatura=temperatura,
        system_prompt=system_prompt,
    )