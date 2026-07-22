# ollama_client.py
import os
import time
from dataclasses import dataclass
from ollama_config import configurar_ollama_token
from ollama import Client, chat

from config import TEMPERATURE_JSON, TEMPERATURE_TEXT
from ollama_config import configurar_ollama_token, obtener_config_ollama





@dataclass
class MetricasLlamada:
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None

_client_instance: Client | None = None

def _cliente() -> Client:
    global _client_instance
    OLLAMA_HOST = os.getenv('OLLAMA_HOST')
    if _client_instance is None:
        host, headers = obtener_config_ollama()
        _client_instance = Client (host=host, headers=headers)
    return _client_instance

def llamar_ollama(
    prompt: str,
    model: str,
    temperatura: float,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    client = _cliente()

    mensajes = []
    if system_prompt:
        mensajes.append({"role": "system", "content": system_prompt})
    mensajes.append({"role": "user", "content": prompt})

    t0 = time.perf_counter()

    response = client.chat(
        model=model,
        messages=mensajes,
        options={
            "temperature": temperatura,
        },
    )

    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    prompt_tokens = response.get("prompt_eval_count")
    output_tokens = response.get("eval_count")
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

    texto = response["message"]["content"]
    return texto, metricas


def llamar_ollama_json(
    prompt: str,
    model: str,
    system_prompt: str | None = None,
) -> tuple[str, MetricasLlamada]:
    return llamar_ollama(
        prompt=prompt,
        model=model,
        temperatura=TEMPERATURE_JSON,
        system_prompt=system_prompt,
    )