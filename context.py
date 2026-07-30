import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def read_faq(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        faq = json.load(f)
    if not isinstance(faq, list):
        raise ValueError("faq_onboarding.json no tiene un formato json válido")
    return faq

def read_docs(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        docs = json.load(f)
    if not isinstance(docs, list):
        raise ValueError("onboarding_docs.json no tiene un formato json válido")
    return docs

def read_empleados(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        empleados = json.load(f)
    if not isinstance(empleados, list):
        raise ValueError("empleados_demo.json no tiene un formato json válido")
    return empleados

def read_empresa(ruta: Path) -> dict:
    with ruta.open(encoding="utf-8") as f:
        empresa = json.load(f)
    if not isinstance(empresa, dict):
        raise ValueError("empresa.json no tiene un formato json válido")
    return empresa

def select_faq(json: list[dict], query: str, max_results: int = 1) -> list[dict]:
    q = (query or "").lower()
    score: list[tuple[int, dict]] = []

    for entry in json:
        s = 0
        for tag in entry.get("tags", []):
            if tag.lower() in q:
                s += 2
        if q in entry.get("pregunta","").lower():
            s += 3
        if s > 0:
            score.append((s, entry))

    score.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in score[:max_results]]

def select_docs(json: list[dict], query: str, max_results: int = 1) -> list[dict]:
    q = (query or "").lower()
    score: list[tuple[int, dict]] = []

    for entry in json:
        s = 0
        for tag in entry.get("tags", []):
            if tag.lower() in q:
                s += 2
        if q in entry.get("titulo", "").lower():
            s += 4
        if q in entry.get("cuerpo", "").lower():
            s += 2

        for token in re.findall(r"[a-záéíóúñ]+", q):
            if token and token in entry.get("cuerpo", "").lower():
                s += 1

        if s > 0:
            score.append((s, entry))

    score.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in score[:max_results]]


def select_docs_by_id(json: list[dict], id: str) -> dict | None:
    return next((e for e in json if e.get("id") == id), None)