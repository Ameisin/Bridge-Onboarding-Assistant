import os
import time
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - import guard for optional dependency
    OpenAI = None  # type: ignore[assignment]

from config import MAX_TOKENS_INPUT, TEMPERATURE_JSON


@dataclass
class MetricasLlamada:
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


_client_instance = None


def _cliente() -> OpenAI:
    global _client_instance
    if _client_instance is None:
        if OpenAI is None:
            raise RuntimeError("El paquete 'openai' no está instalado. Instálalo con pip install openai")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no configurada")
        _client_instance = OpenAI(api_key=api_key)
    return _client_instance


def llamar_openai(
    prompt: str,
    model: str,
    temperatura: float,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    client = _cliente()
    contenido = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"

    t0 = time.perf_counter()
    response = client.responses.create(
        model=model,
        input=contenido,
        temperature=temperatura,
        max_output_tokens=MAX_TOKENS_INPUT,
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    texto = getattr(response, "output_text", "") or ""

    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "input_tokens", None) if usage else None
    output_tokens = getattr(usage, "output_tokens", None) if usage else None
    total_tokens = (
        (prompt_tokens or 0) + (output_tokens or 0)
        if prompt_tokens is not None or output_tokens is not None
        else None
    )

    metricas = MetricasLlamada(
        elapsed_ms=elapsed_ms,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )
    return texto, metricas


def llamar_openai_json(
    prompt: str,
    model: str,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    return llamar_openai(
        prompt=prompt,
        model=model,
        temperatura=TEMPERATURE_JSON,
        system_prompt=system_prompt,
    )
