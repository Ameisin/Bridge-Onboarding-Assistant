# ollama_client.py
import time
from dataclasses import dataclass

import httpx
from ollama import Client

from config import TEMPERATURE_JSON
from ollama_config import obtener_config_ollama


@dataclass
class MetricasLlamada:
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


_client_instance: Client | None = None


def _cliente() -> Client:
    global _client_instance
    if _client_instance is None:
        host, headers = obtener_config_ollama()
        _client_instance = Client(host=host, headers=headers)
    return _client_instance


def verificar_conexion_ollama() -> None:
    client = _cliente()
    try:
        client.list()
    except httpx.ConnectError as e:
        raise RuntimeError('No hay conexión con Ollama en el host configurado.') from e
    except Exception as e:
        raise RuntimeError('Ollama está configurado, pero no responde correctamente.') from e


def llamar_ollama(prompt: str, model: str, temperatura: float, system_prompt: str | None = None) -> tuple[str, MetricasLlamada]:
    client = _cliente()
    mensajes = []
    if system_prompt:
        mensajes.append({'role': 'system', 'content': system_prompt})
    mensajes.append({'role': 'user', 'content': prompt})
    t0 = time.perf_counter()
    try:
        response = client.chat(model=model, messages=mensajes, options={'temperature': temperatura})
    except httpx.ConnectError as e:
        raise RuntimeError('No se pudo conectar a Ollama. Revisa OLLAMA_HOST y que el servicio esté levantado.') from e
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    prompt_tokens = response.get('prompt_eval_count')
    output_tokens = response.get('eval_count')
    total_tokens = ((prompt_tokens or 0) + (output_tokens or 0)) if prompt_tokens is not None or output_tokens is not None else None
    metricas = MetricasLlamada(elapsed_ms=elapsed_ms, prompt_tokens=prompt_tokens, output_tokens=output_tokens, total_tokens=total_tokens)
    return response['message']['content'], metricas


def llamar_ollama_json(prompt: str, model: str, system_prompt: str | None = None) -> tuple[str, MetricasLlamada]:
    return llamar_ollama(prompt=prompt, model=model, temperatura=TEMPERATURE_JSON, system_prompt=system_prompt)
