# benchmark.py
"""Funciones principales del benchmark de modelos"""

import time
import json
# from pathlib import Path

from config import TEMPERATURE_JSON, OUTPUT_DIR, BENCHMARK_MODELS, MIN_PREGUNTAS, PREGUNTAS_PATH
from ollama_client import llamar_ollama
from gemini_client import llamar_gemini

def llamar_modelo(prompt: str, model: str, provider: str, temperatura: float):
    if provider == "ollama":
        return llamar_ollama(
            prompt=prompt,
            model=model,
            temperatura=temperatura,
            system_prompt=None,
        )
    if provider == "gemini":
        return llamar_gemini(
            prompt=prompt,
            model=model,
            temperatura=temperatura,
            system_prompt=None,
        )
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
        """Verifica que el dataset esté correctamente configurado"""
        
        if not self.preguntas_path.exists():
            print(f"◬  No se encontró {self.preguntas_path}")
            return False
        
        try:
            with open(self.preguntas_path, 'r', encoding='utf-8') as f:
                preguntas = json.load(f)
            
            if not isinstance(preguntas, list):
                print("⨉ El archivo de preguntas debe ser una lista")
                return False
            
            if len(preguntas) < self.min_preguntas:
                print(f"⨉ Se necesitan al menos {self.min_preguntas} preguntas, se encontraron {len(preguntas)}")
                return False
            
            # Verificar que cada pregunta tenga los campos necesarios
            for i, pregunta in enumerate(preguntas):
                if not isinstance(pregunta, dict):
                    print(f"⨉ La pregunta {i} no es un diccionario")
                    return False
                
                if 'id' not in pregunta:
                    print(f"⨉ La pregunta {i} no tiene campo 'id'")
                    return False
                
                if 'prompt' not in pregunta:
                    print(f"⨉ La pregunta {i} no tiene campo 'prompt'")
                    return False
                
                if not isinstance(pregunta['id'], str) or not pregunta['id'].strip():
                    print(f"⨉ La pregunta {i} tiene un 'id' inválido")
                    return False
                
                if not isinstance(pregunta['prompt'], str) or not pregunta['prompt'].strip():
                    print(f"⨉ La pregunta {i} tiene un 'prompt' inválido")
                    return False
            
            # Verificar que no haya entradas de ejemplo
            for pregunta in preguntas:
                if 'ejemplo_solo_formato' in pregunta.get('id', ''):
                    print("⨉ Aún hay entradas de ejemplo, elimínalas")
                    return False
            
            print(f"√ Dataset válido ({len(preguntas)} preguntas)")
            return True
            
        except Exception as e:
            print(f"⨉ Error leyendo el dataset: {e}")
            return False

    def validar_entregables(self) -> bool: 
        """Verifica que los entregables estén correctamente configurados"""
        
        # Verificar que exista el directorio de entregables
        if not self.entregables_dir.exists():
            print("◬  Directorio de entregables no encontrado")
            return False
        
        # Verificar archivos necesarios
        matriz_path = self.entregables_dir / "matriz_decision.md"
        recomendacion_path = self.entregables_dir / "recomendacion.md"
        
        if not matriz_path.exists():
            print("◬  No se encontró matriz_decision.md")
            return False
        
        if not recomendacion_path.exists():
            print("◬  No se encontró recomendacion.md")
            return False
        
        # Verificar que los archivos no estén vacíos
        try:
            with open(matriz_path, 'r', encoding='utf-8') as f:
                matriz_content = f.read().strip()
            
            with open(recomendacion_path, 'r', encoding='utf-8') as f:
                recomendacion_content = f.read().strip()
            
            if not matriz_content:
                print("◬  matriz_decision.md está vacío")
                return False
            
            if not recomendacion_content:
                print("◬  recomendacion.md está vacío")  
                return False
                
            print("√ Entregables válidos")
            return True
            
        except Exception as e:
            print(f"⨉ Error verificando entregables: {e}")
            return False

    def validar_todo(self) -> bool: 
        """Verifica todo el benchmark"""
        
        print("Verificación del benchmark...")
        print("-" * 30)
        
        dataset_ok = self.validar_dataset()
        entregables_ok = self.validar_entregables()
        
        if dataset_ok and entregables_ok:
            print("\n√ Todo correcto: benchmark listo para ejecutar")
            return True
        else:
            print("\n⨉ Fallos encontrados en la verificación")
            return False

class BenchmarkRunner:
    def __init__(self, benchmark_models=None, preguntas_path=None, output_dir=None, temperatura=None):
        self.benchmark_models = benchmark_models or BENCHMARK_MODELS
        self.preguntas_path = preguntas_path or PREGUNTAS_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        self.temperatura = temperatura or TEMPERATURE_JSON

    def cargar_preguntas(self) -> list[dict]:
        """Carga las preguntas desde el archivo JSON"""
        if not self.preguntas_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo {self.preguntas_path}")
        
        with open(self.preguntas_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def ejecutar(self) -> tuple[list[dict], dict[str, list[dict]]]:
        """Ejecuta el benchmark con todos los modelos"""
        
        # Cargar las preguntas del benchmark
        preguntas = self.cargar_preguntas()
        resultados = []
        resultados_por_modelo = {}
        
        print("Ejecutando benchmark...")
        print(f"Modelos: {', '.join([model['model'] for model in self.benchmark_models])}")
        print(f"Preguntas: {len(preguntas)}")
        print("-" * 50)
        
        # Procesar modelos secuencialmente
        for model_info in self.benchmark_models:
            model_name = model_info["model"]
            provider = model_info["provider"]
            
            print(f"\n--- Procesando modelo: {model_name} ({provider}) ---")
            resultados_por_modelo[model_name] = []
            
            for i, pregunta in enumerate(preguntas):
                print(f"{i+1}. {pregunta['id']}")
                
                id_pregunta = pregunta['id']
                prompt = pregunta['prompt']
                
                try:
                    print(f"   → {model_name}")
                    
                    t0 = time.perf_counter()
                    texto, metricas = llamar_modelo(
                        prompt=prompt,
                        model=model_name,
                        provider=provider,
                        temperatura=self.temperatura
                    )
                    elapsed_ms = int((time.perf_counter() - t0) * 1000)
                    
                    # Registrar resultado
                    resultado = {
                        "pregunta_id": id_pregunta,
                        "modelo": model_name,
                        "tiempo_ms": elapsed_ms,
                        "tokens_entrada": metricas.prompt_tokens if hasattr(metricas, 'prompt_tokens') else None,
                        "tokens_salida": metricas.output_tokens if hasattr(metricas, 'output_tokens') else None,
                        "tokens_total": metricas.total_tokens if hasattr(metricas, 'total_tokens') else None,
                        "respuesta": texto[:400] + "..." if len(texto) > 400 else texto
                    }
                    
                    resultados.append(resultado)
                    resultados_por_modelo[model_name].append(resultado)
                    
                    print(f"     ▻ {elapsed_ms} ms")
                    
                except Exception as e:
                    print(f"     ⨉ Error con {model_name}: {e}")
                    # Registrar error como resultado con tiempo 0
                    resultado = {
                        "pregunta_id": id_pregunta,
                        "modelo": model_name,
                        "tiempo_ms": 0,
                        "tokens_entrada": None,
                        "tokens_salida": None,
                        "tokens_total": None,
                        "respuesta": f"ERROR: {str(e)}"
                    }
                    resultados.append(resultado)
                    resultados_por_modelo[model_name].append(resultado)
        
        return resultados, resultados_por_modelo

    def guardar_csv(self, resultados: list[dict]) -> str:
        """Guarda los resultados en formato CSV"""
        
        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        import csv
        
        filename = f"benchmark_{time.strftime('%Y%m%d_%H%M%S')}"
        csv_path = self.output_dir / f"{filename}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['pregunta_id', 'modelo', 'tiempo_ms', 'tokens_entrada', 'tokens_salida', 'tokens_total']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for resultado in resultados:
                writer.writerow({
                    'pregunta_id': resultado['pregunta_id'],
                    'modelo': resultado['modelo'],
                    'tiempo_ms': resultado['tiempo_ms'],
                    'tokens_entrada': resultado['tokens_entrada'],
                    'tokens_salida': resultado['tokens_salida']
                    'tokens_totales': resultado['tokebs_total']
                })
        
        print(f"✓ CSV guardado en: {csv_path}")
        return filename

    def generar_reporte(self, resultados: list[dict], resultados_por_modelo: dict[str, list[dict]]) -> str:
        """Genera un informe detallado del benchmark"""
        
        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"report_{time.strftime('%Y%m%d_%H%M%S')}"
        md_path = self.output_dir / f"{filename}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Reporte de Benchmark\n\n")
            f.write(f"Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Parámetros\n\n")
            f.write(f"- Modelos evaluados: {', '.join([model['model'] for model in self.benchmark_models])}\n")
            f.write(f"- Temperatura: {self.temperatura}\n")
            f.write(f"- Total preguntas: {len(resultados) // len(self.benchmark_models)}\n\n")
            
            f.write("## Resultados por pregunta\n\n")
            f.write("| Pregunta | Modelo | Tiempo (ms) | Tokens Entrada | Tokens Salida | Tokens Totales |\n")
            f.write("|----------|--------|-------------|----------------|---------------|---------------|\n")
            
            for resultado in resultados:
                f.write(f"| {resultado['pregunta_id']} | {resultado['modelo']} | {resultado['tiempo_ms']} | {resultado['tokens_entrada']} | {resultado['tokens_salida']} |{resultado['tokens_']} |\n")
        
        print(f"✓ Informe guardado en: {md_path}")
        
        # Generar reportes individuales por modelo
        if resultados_por_modelo:
            for model, model_resultados in resultados_por_modelo.items():
                model_filename = f"report_{model.replace(':', '_')}_{time.strftime('%Y%m%d_%H%M%S')}"
                model_md_path = self.output_dir / f"{model_filename}.md"
                
                with open(model_md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Reporte de Benchmark - Modelo: {model}\n\n")
                    f.write(f"Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("## Preguntas y Respuestas\n\n")
                    
                    for resultado in model_resultados:
                        f.write(f"### Pregunta: {resultado['pregunta_id']}\n")
                        f.write(f"- **Pregunta:** {resultado['pregunta_id']}\n")
                        f.write(f"- **Respuesta:** {resultado['respuesta']}\n\n")
                
                print(f"✓ Reporte individual del modelo {model} guardado en: {model_md_path}")
        
        return filename


class BenchmarkLauncher:
    def __init__(self):
        self.validator = BenchmarkValidator()
        self.runner = BenchmarkRunner()

    def launch(self) -> None:
        """Ejecuta todo el benchmark"""
        print("=== Benchmark de modelos para Employee Onboarding Assistant ===\n")
        
        # Verificar dataset 
        print("0) Verificación (sin API)")
        try:
            preguntas_ok = self.validator.validar_dataset()
            if preguntas_ok:
                print("  [OK] data/preguntas.json")
            else:
                print("  [PENDIENTE — preguntas]")
                return
        except Exception as e:
            print(f"  [ERROR] {e}")
            return
        
        # Verificar entregables
        try:
            entregables_ok = self.validator.validar_entregables()
            if entregables_ok:
                print("  [OK] entregables/")
            else:
                print("  [PENDIENTE — entregables] (Fase 2)")
        except Exception as e:
            print(f"  [ERROR] {e}")
            return

        print("\n1) Benchmark ejecutándose (puede tardar varios minutos)...")
        
        try:
            # Ejecutar el benchmark
            resultados, resultados_por_modelo = self.runner.ejecutar()

            
            if resultados:
                # Generar reporte
                nombre_archivo = self.runner.generar_reporte(resultados, resultados_por_modelo)
                print(f"\n√ Benchmark completado exitosamente")
                nombre_archivo = self.runner.guardar_csv(resultados)
                print(f"√ CSV: output/{nombre_archivo}.csv")
                print(f"√ Informe: output/{nombre_archivo}.md")
            else:
                print("⨉ No se obtuvieron resultados")
                
        except Exception as e:
            print(f"⨉ Error ejecutando el benchmark: {e}")
            return
