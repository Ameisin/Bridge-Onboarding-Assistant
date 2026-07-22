"""config.py - constantes y reglas globales del proyecto.

Qué hace este módulo:
  - Define modelo a utilizar, temperaturas, límites de caracteres/tokens.
  - Lista categorías y prioridades permitidas (whitelist).
  - Guarda mensajes estándar de éxito y error.
  - Define variable de sistema ocupado (SYS_BUSY).
  - Configuración del benchmark

Para qué sirve:
  - Un solo sitio para cambiar parámetros sin tocar la lógica de cada función.
  - Lo importan `validators.py`, `logic.py`, y conectores con LLM.

Se puede modificar el archivo salvo:
  - Normalmente no se modifica este archivo, únicamente para cambiar el modelo.
"""


from pathlib import Path


MODEL = ''
TEMPERATURE_TEXT = 0.1
TEMPERATURE_JSON = 0



DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"

EMPRESA_PATH = DATA_DIR / "empresa.json"
DOCS_PATH = DATA_DIR / "onboarding_docs.json"
FAQ_PATH = DATA_DIR / "faq_onboarding.json"
EMPLEADOS_PATH = DATA_DIR / "empleados_demo.json"
PREGUNTAS_PATH = DATA_DIR / "preguntas_benchmark.json"

MIN_PREGUNTAS = 6

BENCHMARK_MODELS = [
    {"provider": "ollama", "model": "qwen3.5:9b"},   
    {"provider": "ollama", "model": "glm-4.7-flash:q4_K_M"},
    {"provider": "ollama", "model": "gpt-oss-safeguard:20b"},
]

