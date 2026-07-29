import os
import time
from dataclasses import dataclass

try:
    from huggingface_hub import InferenceClient
except ImportError:  # pragma: no cover - import guard for optional dependency
    InferenceClient = None  # type: ignore[assignment]

from config import MAX_TOKENS_INPUT, TEMPERATURE_JSON


@dataclass
class MetricasLlamada:
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


_client_instance = None


def _cliente():
    global _client_instance
    if _client_instance is None:
        if InferenceClient is None:
            raise RuntimeError("El paquete 'huggingface_hub' no está instalado. Instálalo con pip install huggingface_hub")
        token = os.getenv("HF_TOKEN", "").strip()
        if not token:
            raise RuntimeError("HF_TOKEN no configurado")
        _client_instance = InferenceClient(api_key=token)
    return _client_instance


def llamar_huggingface(
    prompt: str,
    model: str,
    temperatura: float,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    client = _cliente()
    contenido = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"

    t0 = time.perf_counter()
    response = client.chat_completion(
        model=model,
        messages=[{"role": "user", "content": contenido}],
        temperature=temperatura,
        max_tokens=MAX_TOKENS_INPUT,
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    texto = response.choices[0].message.content if getattr(response, "choices", None) else ""
    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
    output_tokens = getattr(usage, "completion_tokens", None) if usage else None
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


def llamar_huggingface_json(
    prompt: str,
    model: str,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    return llamar_huggingface(
        prompt=prompt,
        model=model,
        temperatura=TEMPERATURE_JSON,
        system_prompt=system_prompt,
    )
