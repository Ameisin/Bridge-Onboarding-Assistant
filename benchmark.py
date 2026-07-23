# benchmark.py
import json
import time
from pathlib import Path
import csv

from config import (
    BENCHMARK_TEMPERATURE,
    OUTPUT_DIR,
    BENCHMARK_MODELS,
    PREGUNTAS_PATH,
    ENTREGABLES_DIR,
    MIN_PREGUNTAS,
)
from ollama_client import llamar_ollama, verificar_conexion_ollama
from gemini_client import llamar_gemini


def llamar_modelo(prompt: str, model: str, provider: str, temperatura: float):
    provider = provider.lower()
    if provider == "ollama":
        return llamar_ollama(prompt=prompt, model=model, temperatura=temperatura, system_prompt=None)
    if provider == "gemini":
        return llamar_gemini(prompt=prompt, model=model, temperatura=temperatura, system_prompt=None)
    raise ValueError(f"Proveedor no soportado: {provider}")


class BenchmarkValidator:
    def __init__(
        self,
        preguntas_path: Path = PREGUNTAS_PATH,
        entregables_dir: Path = ENTREGABLES_DIR,
        min_preguntas: int = MIN_PREGUNTAS,
    ) -> None:
        self.preguntas_path = preguntas_path
        self.entregables_dir = entregables_dir
        self.min_preguntas = min_preguntas

    def validar_dataset(self) -> bool:
        if not self.preguntas_path.exists():
            print(f"◬ No se encontró {self.preguntas_path}")
            return False
        try:
            with open(self.preguntas_path, "r", encoding="utf-8") as f:
                preguntas = json.load(f)
            if not isinstance(preguntas, list):
                print("⨉ El archivo de preguntas debe ser una lista")
                return False
            if len(preguntas) < self.min_preguntas:
                print(f"⨉ Se necesitan al menos {self.min_preguntas} preguntas, se encontraron {len(preguntas)}")
                return False
            for i, pregunta in enumerate(preguntas):
                if not isinstance(pregunta, dict):
                    print(f"⨉ La pregunta {i} no es un diccionario")
                    return False
                if "id" not in pregunta:
                    print(f"⨉ La pregunta {i} no tiene campo 'id'")
                    return False
                if "prompt" not in pregunta:
                    print(f"⨉ La pregunta {i} no tiene campo 'prompt'")
                    return False
                if not isinstance(pregunta["id"], str) or not pregunta["id"].strip():
                    print(f"⨉ La pregunta {i} tiene un 'id' inválido")
                    return False
                if not isinstance(pregunta["prompt"], str) or not pregunta["prompt"].strip():
                    print(f"⨉ La pregunta {i} tiene un 'prompt' inválido")
                    return False
            print(f"√ Dataset válido ({len(preguntas)} preguntas)")
            return True
        except Exception as e:
            print(f"⨉ Error leyendo el dataset: {e}")
            return False

    def validar_entregables(self) -> bool:
        if not self.entregables_dir.exists():
            print("◬ Directorio de entregables no encontrado")
            return False
        matriz_path = self.entregables_dir / "matriz_decision.md"
        recomendacion_path = self.entregables_dir / "recomendacion.md"
        if not matriz_path.exists():
            print("◬ No se encontró matriz_decision.md")
            return False
        if not recomendacion_path.exists():
            print("◬ No se encontró recomendacion.md")
            return False
        try:
            if not matriz_path.read_text(encoding="utf-8").strip():
                print("◬ matriz_decision.md está vacío")
                return False
            if not recomendacion_path.read_text(encoding="utf-8").strip():
                print("◬ recomendacion.md está vacío")
                return False
            print("√ Entregables válidos")
            return True
        except Exception as e:
            print(f"⨉ Error verificando entregables: {e}")
            return False

    def validar_todo(self) -> bool:
        print("Verificación del benchmark...")
        print("-" * 30)
        dataset_ok = self.validar_dataset()
        entregables_ok = self.validar_entregables()
        if dataset_ok and entregables_ok:
            print("\n√ Todo correcto: benchmark listo para ejecutar")
            return True
        print("\n⨉ Fallos encontrados en la verificación")
        return False


class BenchmarkRunner:
    def __init__(self, benchmark_models=None, preguntas_path=None, output_dir=None, temperatura=None):
        self.benchmark_models = benchmark_models or BENCHMARK_MODELS
        self.preguntas_path = preguntas_path or PREGUNTAS_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        self.temperatura = temperatura or BENCHMARK_TEMPERATURE

    def cargar_preguntas(self) -> list[dict]:
        if not self.preguntas_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo {self.preguntas_path}")
        with open(self.preguntas_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def ejecutar(self) -> tuple[list[dict], dict[str, list[dict]]]:
        preguntas = self.cargar_preguntas()
        resultados = []
        resultados_por_modelo = {}

        print("Ejecutando benchmark...")
        print(f"Modelos: {', '.join([m['model'] for m in self.benchmark_models])}")
        print(f"Preguntas: {len(preguntas)}")
        print("-" * 50)

        for model_info in self.benchmark_models:
            model_name = model_info["model"]
            provider = model_info["provider"]

            print(f"\n--- Procesando modelo: {model_name} ({provider}) ---")
            resultados_por_modelo[model_name] = []

            if provider == "ollama":
                verificar_conexion_ollama()

            for pregunta in preguntas:
                id_pregunta = pregunta["id"]
                prompt = pregunta["prompt"]

                try:
                    texto, metricas = llamar_modelo(
                        prompt=prompt,
                        model=model_name,
                        provider=provider,
                        temperatura=self.temperatura,
                    )
                    resultado = {
                        "pregunta_id": id_pregunta,
                        "modelo": model_name,
                        "tiempo_ms": metricas.elapsed_ms,
                        "tokens_entrada": metricas.prompt_tokens,
                        "tokens_salida": metricas.output_tokens,
                        "respuesta": texto[:400] + "..." if len(texto) > 400 else texto,
                    }
                except Exception as e:
                    resultado = {
                        "pregunta_id": id_pregunta,
                        "modelo": model_name,
                        "tiempo_ms": 0,
                        "tokens_entrada": None,
                        "tokens_salida": None,
                        "respuesta": f"ERROR: {e}",
                    }

                resultados.append(resultado)
                resultados_por_modelo[model_name].append(resultado)

        return resultados, resultados_por_modelo

    def guardar_csv(self, resultados: list[dict]) -> str:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"benchmark_{time.strftime('%Y%m%d_%H%M%S')}"
        csv_path = self.output_dir / f"{filename}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["pregunta_id", "modelo", "tiempo_ms", "tokens_entrada", "tokens_salida", "respuesta"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for resultado in resultados:
                writer.writerow(resultado)

        print(f"✓ CSV guardado en: {csv_path}")
        return filename

    def generar_reporte(self, resultados: list[dict], resultados_por_modelo: dict[str, list[dict]]) -> str:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"report_{time.strftime('%Y%m%d_%H%M%S')}"
        md_path = self.output_dir / f"{filename}.md"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Reporte de Benchmark\n\n")
            f.write(f"Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Resultados por pregunta\n\n")
            f.write("| Pregunta | Modelo | Tiempo (ms) | Tokens Entrada | Tokens Salida |\n")
            f.write("|----------|--------|-------------|----------------|---------------|\n")
            for r in resultados:
                f.write(f"| {r['pregunta_id']} | {r['modelo']} | {r['tiempo_ms']} | {r['tokens_entrada']} | {r['tokens_salida']} |\n")

        print(f"✓ Informe guardado en: {md_path}")
        return filename


class BenchmarkLauncher:
    def __init__(self):
        self.validator = BenchmarkValidator()
        self.runner = BenchmarkRunner()

    def launch(self) -> None:
        print("=== Benchmark de modelos para Employee Onboarding Assistant ===\n")

        print("0) Verificación (sin API)")
        if not self.validator.validar_dataset():
            print(" [PENDIENTE — preguntas]")
            return
        if not self.validator.validar_entregables():
            print(" [PENDIENTE — entregables] (Fase 2)")
            return

        print("\n1) Benchmark ejecutándose (puede tardar varios minutos)...")

        try:
            resultados, resultados_por_modelo = self.runner.ejecutar()
            if resultados:
                nombre_archivo = self.runner.guardar_csv(resultados)
                self.runner.generar_reporte(resultados, resultados_por_modelo)
                print("\n√ Benchmark completado exitosamente")
                print(f" - {len(resultados)} resultados procesados")
                print(f" - CSV: output/{nombre_archivo}.csv")
                print(f" - Informe: output/{nombre_archivo}.md")
            else:
                print("⨉ No se obtuvieron resultados")
        except Exception as e:
            print(f"⨉ Error ejecutando el benchmark: {e}")


if __name__ == "__main__":
    BenchmarkLauncher().launch()