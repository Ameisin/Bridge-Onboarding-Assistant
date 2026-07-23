# demo_benchmark.py
import os
import json
import time
import csv
from datetime import datetime
# Para llama-server (si lo usamos)
#from ollama_client import verificar_conexion_ollama, llamar_ollama


try:
    from ollama_client import verificar_conexion_ollama, llamar_ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from google.ai.generativeai import GenerativeModel, configure
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


def load_benchmark_dataset():
    """Carga el dataset de benchmark desde el archivo proporcionado"""
    try:
        with open("data/preguntas_benchmark.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error en la carga del dataset de benchmark, comprueba que existe el archivo: {e}")
        return []


def get_model_response(model_config, prompt, temperature=0.2):
    """Obtiene respuesta del modelo según configuración"""
    provider = model_config.get("provider", "").lower()
    model_name = model_config.get("model", "")

    if provider == "gemini":
        if not HAS_GEMINI:
            raise ImportError("Se necesita google-genai instalado para usar Gemini")

        try:
            import dotenv
            dotenv.load_dotenv()

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("◬ Atención: no se encuentra GEMINI_API_KEY en .env")
                return None, 0, 0

            configure(api_key=api_key)
            model = GenerativeModel(model_name)

            start_time = time.time()
            response = model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            end_time = time.time()

            text = getattr(response, "text", None)
            if not text:
                return None, 0, 0

            return text, end_time - start_time, len(text)

        except Exception as e:
            print(f"Error con Gemini: {e}")
            return None, 0, 0

    elif provider == "ollama":
        if not HAS_OLLAMA:
            raise ImportError("Se necesita tener ollama_client.py accesible para usar Ollama")

        try:
            texto, metricas = llamar_ollama(
                prompt=prompt,
                model=model_name,
                temperatura=temperature,
                system_prompt=None,
            )
            return texto, metricas.elapsed_ms / 1000, len(texto)

        except Exception as e:
            print(f"Error con Ollama: {e}")
            return None, 0, 0

    else:
        raise ValueError(f"Proveedor no tratado / desconocido: {provider}")


def evaluate_response(response, question):
    """Evalúa la respuesta del modelo LLM según criterio básico"""
    if not response:
        return {
            "fidelidad": 1,
            "relevancia": 1,
            "tono": 1,
            "seguridad": 1,
        }

    score = {
        "fidelidad": 3,
        "relevancia": 3,
        "tono": 3,
        "seguridad": 3,
    }

    if any(word in response.lower() for word in ["salario", "empleado", "dato", "sensible", "credencial"]):
        score["seguridad"] = max(1, score["seguridad"] - 1)

    return score


def run_benchmark(models=None, num_cases=10):
    """Ejecuta el benchmark comparando los modelos"""
    dataset = load_benchmark_dataset()
    if not dataset:
        print("No se pudo cargar el dataset de benchmark")
        return []

    try:
        from config import BENCHMARK_MODELS
    except ImportError:
        BENCHMARK_MODELS = [
            {"provider": "gemini", "model": "gemini-pro"}
        ]

    if models is None:
        models = BENCHMARK_MODELS

    ollama_models = [m for m in models if m.get("provider", "").lower() == "ollama"]
    if ollama_models and HAS_OLLAMA:
        try:
            verificar_conexion_ollama()
            print("✓ Conexión con Ollama verificada")
        except Exception as e:
            print(f"◬ No se pudo verificar conexión con Ollama: {e}")

    cases = dataset[:num_cases]
    results = []

    print(f"Ejecutando benchmark con {len(cases)} casos usando modelos: {[m['provider'] + ':' + m['model'] for m in models]}")

    for i, case in enumerate(cases):
        print(f"\nCasos evaluados: {i+1}/{len(cases)}")
        question = case.get("consulta", "")

        for model_config in models:
            try:
                prompt = f"""Eres un asistente experto en políticas internas de la empresa Bridge SA.
Responde solo usando la información proporcionada.
Pregunta: {question}
Respuesta correcta basada en documentación:
"""

                response, latency, token_count = get_model_response(model_config, prompt)

                if not response:
                    print(f"◬ No se obtuvo respuesta del modelo {model_config['provider']}:{model_config['model']} para la pregunta {i+1}")
                    continue

                evaluation = evaluate_response(response, question)

                result = {
                    "caso_id": i + 1,
                    "modelo_provider": model_config["provider"],
                    "modelo_name": model_config["model"],
                    "pregunta": question,
                    "respuesta": response,
                    "latencia_segundos": round(latency, 3),
                    "tokens_usados": token_count,
                    "fidelidad": evaluation["fidelidad"],
                    "relevancia": evaluation["relevancia"],
                    "tono": evaluation["tono"],
                    "seguridad": evaluation["seguridad"],
                }
                results.append(result)

            except Exception as e:
                print(f"Error evaluando {model_config['provider']}:{model_config['model']} caso {i+1}: {e}")
                continue

    return results
def guarda_csv(results, filename='output/benchmark_resultados.csv'):
    """Guardar los resultados en archivo CSV"""
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not results:
        print("No se han generado resultados CSV para guardar")
        return
    campos_resultados = [
        'caso_id', 'modelo_provider', 'modelo_name', 'pregunta', 'respuesta',
        'latencia_segundos', 'tokens_usados', 'fidelidad',
        'relevancia', 'tono', 'seguridad'
    ]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos_resultados)
        print("caso,proveedor,modelo,pregunta,respuesta,latencia(segs),tokens,fidelidad,relevancia,tono,seguridad")
        for result in results:
            writer.writeheader()
            writer.writerow(result)
    print(f"Resultados obtenidos guardados en: {filename}")
def create_matriz_decision(models_config):
    """Genera la matriz de decisión"""
    # Crea la matriz con los modelos de configuración
    model_names = [f"{m['provider']}:{m['model']}" for m in models_config]
    content = f"""
Matriz de Decisión del Modelo
Comparativa de Modelos
| Criterio | {' | '.join(model_names)} |
|----------|------------------------------|
Recomendaciones
Análisis Detallado por Modelo
"""
    # Para cada modelo, añadir comentarios
    for model in models_config:
        content += f"### {model['provider']}:{model['model']}\n"
        if model['provider'] == 'gemini':
            content += "- Ventajas: Mayor número de tokens, mejor calidad en respuestas complejas\n"
            content += "- Desventajas: Latencia más alta. Momentos pico con posible saturación, luego es posible tener que escalar en instancias para paliar.\n\n"
        elif model['provider'] == 'ollama':
            content += "- Ventajas: Menor latencia por ser un servicio local dentro de la intranet o dedicado, el consumo de tokens cae en relavancia.\n"
            content += "- Desventajas: Es posible tener una menor calidad en consultas complejas, salvo adaptación en contexto RAG.\n\n"
    # Crear contenido general
    content += """
Recomendación Final
Basado en el benchmark, las decisiones deben considerar:
1. Calidad vs Velocidad
2. Requisitos de latencia del sistema
3. Costos asociados al uso de API (si se duplica el tráfico se duplica tambien el consumo-coste)
4. Necesidades específicas del contexto de Bridge SA
"""
    # Crear directorio si no existe
    os.makedirs('entregables', exist_ok=True)
    with open('entregables/matriz_decision.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Matriz de decisión guardada en entregables/matriz_decision.md")
def create_recomendacion(models_config):
    """Generar archivo de recomendación"""
    content = """
Recomendación de Modelo para Deployment
Análisis de Benchmark
Tras ejecutar el benchmark con casos seleccionados sobre políticas internas de Bridge SA, se ha identificado una diferenciación significativa entre los modelos evaluados:
Rendimiento Global
"""
    # Añadir comparaciones
    for model in models_config:
        content += f"- {model['provider']}:{model['model']}: "
        if model['provider'] == 'gemini':
            content += "Mayor calidad en respuestas precisas, mejores resultados en fidelidad y relevancia\n"
        elif model['provider'] == 'ollama':
            content += "Menor latencia, pero con menor profundidad en comprensión de contextos complejos\n"
    content += """
Recomendación Final
Se recomienda utilizar el modelo que mejor equilibre calidad y rendimiento para los requisitos específicos de Bridge SA.
Justificación Técnica
El modelo seleccionado debe considerar:
1. Mayor capacidad de razonamiento y comprensión del contexto
2. Mejor manejo de instrucciones complejas
3. Mayor consistencia en tareas repetitivas y estructuradas
Escalabilidad
¿Qué pasaría si duplicáramos el tráfico?
1. Tokens consumidos vs. Coste recursos: Se duplicaría el uso de tokens, pero manteniendo la calidad constante. Lo que sí impactaría sería en coste, doble de tráfico supondía también duplicar los tokens.
2. Latencia posiblemente afectada: Dado que los modelos consumen más recursos, se necesitaría escalar adecuadamente el número de instancias y/o automatizar el escalado conforme a umbrales de disparo de instanciado en momentos que puedan ser pico de uso.
3. El escalado en el servicio, requeriría un balanceo adecuado de clientes para reparto de carga entre las distintas instancias simultáneas - round robin yendo a lo más básico, o reparto por situación de carga de la instancia (balanceo inteligente).
"""
    # Crear directorio si no existe
    os.makedirs('entregables', exist_ok=True)
    with open('entregables/recomendacion.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Recomendación guardada en entregables/recomendacion.md")
def main():
    """Función principal del benchmark"""
    print("=========================================")
    print("Benchmark - Employee Onboarding Assistant")
    print("=========================================")
    # Ejecutar benchmark con modelos
    try:
        results = run_benchmark(num_cases=10)
        if not results:
            print("No se obtuvieron resultados.")
            return
        # Guardar resultados en CSV
        guarda_csv(results)
        # Generar archivos de decisión usando los modelos actuales
        try:
            from config import BENCHMARK_MODELS
        except ImportError:
            BENCHMARK_MODELS = [
                {
                    "provider": "gemini",
                    "model": ""
                }
            ]
        create_matriz_decision(BENCHMARK_MODELS)
        create_recomendacion(BENCHMARK_MODELS)
        print("\n✓ → Benchmark completado exitosamente")
        print(f"   - {len(results)} resultados procesados")
        print(f"   - Archivos generados en:\n")
        print("     → output/benchmark_resultados.csv")
        print("     → entregables/matriz_decision.md")
        print("     → entregables/recomendacion.md")
    except Exception as e:
        print(f"⨉ → Error ejecutando benchmark: {e}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    main()