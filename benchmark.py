# benchmark.py
"""Funciones principales del benchmark de modelos"""
import os
import time
import json
from pathlib import Path

from config import BENCHMARK_TEMPERATURE, OUTPUT_DIR, BENCHMARK_MODELS, PREGUNTAS_PATH, ENTREGABLES_DIR, MIN_PREGUNTAS
from ollama_client import llamar_ollama
from gemini_client import llamar_gemini
from openai_client import llamar_openai
from huggingface_client import llamar_huggingface


def obtener_tipo_pregunta(pregunta: dict | None) -> str:
    """Devuelve el tipo de pregunta a partir del id o de un campo explícito."""
    if not isinstance(pregunta, dict):
        return "desconocido"

    tipo = pregunta.get("tipo")
    if isinstance(tipo, str) and tipo.strip():
        return tipo.strip()

    identificador = str(pregunta.get("id", "")).strip().lower()
    if identificador.startswith("dominio"):
        return "dominio"
    if identificador.startswith("ambig"):
        return "ambigüedad"
    if identificador.startswith("limite"):
        return "limite"
    return "desconocido"


def obtener_objetivo_pregunta(pregunta: dict | None) -> str:
    """Devuelve el objetivo de la pregunta si viene explícitamente en el dataset."""
    if not isinstance(pregunta, dict):
        return ""

    objetivo = pregunta.get("objetivo")
    if isinstance(objetivo, str) and objetivo.strip():
        return objetivo.strip()
    return ""


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
    if provider == "openai":
        return llamar_openai(
            prompt=prompt,
            model=model,
            temperatura=temperatura,
            system_prompt=None,
        )
    if provider == "huggingface":
        return llamar_huggingface(
            prompt=prompt,
            model=model,
            temperatura=temperatura,
            system_prompt=None,
        )
    raise ValueError(f"Proveedor no soportado: {provider}")


def detectar_error_modelo_no_encontrado(exc: Exception) -> bool:
    """Detecta patrones comunes de error cuando un modelo no existe o no está disponible."""
    mensaje = str(exc).lower()
    return any(token in mensaje for token in ["model not found", "not found", "404", "no such model", "does not exist", "doesn't exist"])


def llamar_modelo_con_fallback(
    prompt: str,
    model: str,
    provider: str,
    temperatura: float,
    modelos_disponibles: list[dict],
    llamar_modelo_fn=None,
):
    """Prueba el modelo solicitado y, si falta, intenta el siguiente modelo del listado."""
    if llamar_modelo_fn is None:
        llamar_modelo_fn = llamar_modelo

    modelos_a_probar = []
    for modelo in modelos_disponibles:
        if modelo.get("provider") == provider:
            modelos_a_probar.append(modelo)

    if not modelos_a_probar:
        return llamar_modelo_fn(prompt=prompt, model=model, provider=provider, temperatura=temperatura), model

    start_index = 0
    for idx, modelo in enumerate(modelos_a_probar):
        if modelo.get("model") == model:
            start_index = idx
            break

    for modelo in modelos_a_probar[start_index:]:
        candidato = modelo.get("model")
        if candidato == model:
            try:
                return llamar_modelo_fn(prompt=prompt, model=candidato, provider=provider, temperatura=temperatura), candidato
            except Exception as exc:
                if not detectar_error_modelo_no_encontrado(exc):
                    raise
                print(f"   ↳ Modelo no disponible: {candidato}. Se probará el siguiente.")
                continue
        else:
            try:
                return llamar_modelo_fn(prompt=prompt, model=candidato, provider=provider, temperatura=temperatura), candidato
            except Exception as exc:
                if not detectar_error_modelo_no_encontrado(exc):
                    raise
                print(f"   ↳ Modelo no disponible: {candidato}. Se probará el siguiente.")
                continue

    raise RuntimeError(f"No fue posible ejecutar ninguno de los modelos disponibles para {provider}")


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
        self.temperatura = temperatura or BENCHMARK_TEMPERATURE

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
                tipo_pregunta = obtener_tipo_pregunta(pregunta)
                objetivo_pregunta = obtener_objetivo_pregunta(pregunta)
                
                try:
                    print(f"   → {model_name}")
                    
                    t0 = time.perf_counter()
                    resultado_llamada, modelo_utilizado = llamar_modelo_con_fallback(
                        prompt=prompt,
                        model=model_name,
                        provider=provider,
                        temperatura=self.temperatura,
                        modelos_disponibles=self.benchmark_models,
                    )
                    texto, metricas = resultado_llamada
                    if modelo_utilizado != model_name:
                        print(f"     ↳ Fallback aplicado a: {modelo_utilizado}")
                    elapsed_ms = int((time.perf_counter() - t0) * 1000)
                    prompt_tokens = metricas.prompt_tokens if hasattr(metricas, 'prompt_tokens') else None
                    output_tokens = metricas.output_tokens if hasattr(metricas, 'output_tokens') else None
                    total_tokens = (
                        (prompt_tokens or 0) + (output_tokens or 0)
                        if prompt_tokens is not None or output_tokens is not None
                        else None
                    )
                    tokens_per_second = None
                    if elapsed_ms and total_tokens is not None and total_tokens > 0:
                        tokens_per_second = round(total_tokens / (elapsed_ms / 1000), 2)
                    
                    # Registrar resultado
                    resultado = {
                        "pregunta_id": id_pregunta,
                        "tipo_pregunta": tipo_pregunta,
                        "objetivo_pregunta": objetivo_pregunta,
                        "modelo": modelo_utilizado,
                        "tiempo_ms": elapsed_ms,
                        "tokens_entrada": prompt_tokens,
                        "tokens_salida": output_tokens,
                        "tokens_totales": total_tokens,
                        "tokens_por_segundo": tokens_per_second,
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
                        "tipo_pregunta": tipo_pregunta,
                        "objetivo_pregunta": objetivo_pregunta,
                        "modelo": modelo_utilizado if 'modelo_utilizado' in locals() else model_name,
                        "tiempo_ms": 0,
                        "tokens_entrada": None,
                        "tokens_salida": None,
                        "tokens_totales": None,
                        "tokens_por_segundo": None,
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
            fieldnames = [
                'pregunta_id',
                'tipo_pregunta',
                'objetivo_pregunta',
                'modelo',
                'tiempo_ms',
                'tokens_entrada',
                'tokens_salida',
                'tokens_totales',
                'tokens_por_segundo',
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for resultado in resultados:
                writer.writerow({
                    'pregunta_id': resultado['pregunta_id'],
                    'tipo_pregunta': resultado.get('tipo_pregunta', ''),
                    'objetivo_pregunta': resultado.get('objetivo_pregunta', ''),
                    'modelo': resultado['modelo'],
                    'tiempo_ms': resultado['tiempo_ms'],
                    'tokens_entrada': resultado.get('tokens_entrada'),
                    'tokens_salida': resultado.get('tokens_salida'),
                    'tokens_totales': resultado.get('tokens_totales'),
                    'tokens_por_segundo': resultado.get('tokens_por_segundo'),
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
            f.write("| Pregunta | Tipo | Objetivo | Modelo | Tiempo (ms) | Tokens Entrada | Tokens Salida | Tokens Totales | Tokens/s |\n")
            f.write("|----------|------|----------|--------|-------------|----------------|---------------|----------------|----------|\n")
            
            for resultado in resultados:
                tipo_pregunta = resultado.get('tipo_pregunta', obtener_tipo_pregunta(resultado))
                objetivo_pregunta = resultado.get('objetivo_pregunta', obtener_objetivo_pregunta(resultado))
                f.write(
                    f"| {resultado['pregunta_id']} | {tipo_pregunta} | {objetivo_pregunta} | {resultado['modelo']} | {resultado['tiempo_ms']} | "
                    f"{resultado.get('tokens_entrada')} | {resultado.get('tokens_salida')} | {resultado.get('tokens_totales')} | {resultado.get('tokens_por_segundo')} |\n"
                )

            f.write("\n## Resumen por modelo\n\n")
            for model, model_resultados in resultados_por_modelo.items():
                tiempos = [r.get('tiempo_ms') or 0 for r in model_resultados]
                tokens_totales = [r.get('tokens_totales') or 0 for r in model_resultados]
                tokens_entrada = [r.get('tokens_entrada') or 0 for r in model_resultados]
                tokens_salida = [r.get('tokens_salida') or 0 for r in model_resultados]
                total_tiempo = sum(tiempos)
                total_tokens = sum(tokens_totales)
                total_tokens_entrada = sum(tokens_entrada)
                total_tokens_salida = sum(tokens_salida)
                media_tiempo = round(total_tiempo / len(model_resultados), 2) if model_resultados else 0
                media_tokens_s = round(total_tokens / (total_tiempo / 1000), 2) if total_tiempo > 0 and total_tokens > 0 else 0

                f.write(f"### {model}\n")
                f.write(f"- Preguntas evaluadas: {len(model_resultados)}\n")
                f.write(f"- Tiempo total (ms): {total_tiempo}\n")
                f.write(f"- Tiempo medio por pregunta (ms): {media_tiempo}\n")
                f.write(f"- Tokens totales: {total_tokens}\n")
                f.write(f"- Tokens de entrada totales: {total_tokens_entrada}\n")
                f.write(f"- Tokens de salida totales: {total_tokens_salida}\n")
                f.write(f"- Tokens/s promedio: {media_tokens_s}\n\n")
        
        print(f"✓ Informe guardado en: {md_path}")
        
        # Generar reportes individuales por modelo
        if resultados_por_modelo:
            for model, model_resultados in resultados_por_modelo.items():
                model_filename = f"report_{model.replace(':', '_').replace('/', '_')}_{time.strftime('%Y%m%d_%H%M%S')}"
                model_md_path = self.output_dir / f"{model_filename}.md"
                
                with open(model_md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Reporte de Benchmark - Modelo: {model}\n\n")
                    f.write(f"Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("## Preguntas y Respuestas\n\n")
                    
                    for resultado in model_resultados:
                        tipo_pregunta = resultado.get('tipo_pregunta', obtener_tipo_pregunta(resultado))
                        objetivo_pregunta = resultado.get('objetivo_pregunta', obtener_objetivo_pregunta(resultado))
                        f.write(f"### Pregunta: {resultado['pregunta_id']}\n")
                        f.write(f"- **Pregunta:** {resultado['pregunta_id']}\n")
                        f.write(f"- **Tipo:** {tipo_pregunta}\n")
                        f.write(f"- **Objetivo:** {objetivo_pregunta}\n")
                        f.write(f"- **Tokens totales:** {resultado.get('tokens_totales')}\n")
                        f.write(f"- **Tokens/s:** {resultado.get('tokens_por_segundo')}\n")
                        f.write(f"- **Respuesta:** {resultado['respuesta']}\n\n")
                
                print(f"✓ Reporte individual del modelo {model} guardado en: {model_md_path}")
        
        return filename
    
def create_matriz_decision(models_config, resultados_por_modelo=None, output_dir=None):
    """Genera la matriz de decisión con un criterio claro de ranking."""
    output_dir = Path(output_dir or 'entregables')
    output_dir.mkdir(parents=True, exist_ok=True)

    model_names = [f"{m['provider']}:{m['model']}" for m in models_config]
    content = f"""# Matriz de Decisión del Modelo

## Comparativa de Modelos

| Criterio | {' | '.join(model_names)} |
|----------|------------------------------|
| Tipo | {' | '.join(['API externa' if m['provider'] == 'gemini' else 'Local/privado' for m in models_config])} |
| Coste por token | {' | '.join(['Mayor coste por token' if m['provider'] == 'gemini' else 'Menor coste operativa' for m in models_config])} |
| Latencia | {' | '.join(['Media/alta' if m['provider'] == 'gemini' else 'Baja' for m in models_config])} |
| Calidad en tareas complejas | {' | '.join(['Alta' if m['provider'] == 'gemini' else 'Media' for m in models_config])} |

## Recomendaciones
"""

    for model in models_config:
        name = f"{model['provider']}:{model['model']}"
        content += f"### {name}\n"
        if model['provider'] == 'gemini':
            content += "- Ventajas: suele ofrecer mejor precisión y mayor robustez en respuestas complejas.\n"
            content += "- Desventajas: coste por token mayor y latencia más sensible a picos de tráfico.\n\n"
        elif model['provider'] == 'ollama':
            content += "- Ventajas: menor latencia, mejor control de despliegue local y menor coste operativo.\n"
            content += "- Desventajas: puede ser menos consistente en tareas muy complejas si no hay adaptación de contexto.\n\n"

    content += """
## Recomendación Final

Si existe un modelo local coherente con el rendimiento mínimo requerido, debe preferirse para la adopción inicial porque ofrece mejor relación coste/latencia y mayor control operativo. Solo se recomienda un modelo externo si aporta una mejora claramente superior en calidad o robustez para casos críticos.

Criterios de decisión:
1. Calidad en tareas de onboarding, límites y ambigüedad.
2. Latencia percibida por el usuario.
3. Coste por token y sostenibilidad operativa.
4. Facilidad de integración y control del entorno.
"""

    with open(output_dir / 'matriz_decision.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Matriz de decisión guardada en {output_dir / 'matriz_decision.md'}")


def create_recomendacion(models_config, resultados_por_modelo=None, output_dir=None):
    """Genera una recomendación con ranking explícito y criterios claros."""
    output_dir = Path(output_dir or 'entregables')
    output_dir.mkdir(parents=True, exist_ok=True)

    if resultados_por_modelo is None:
        resultados_por_modelo = {}

    ranking = []
    for model in models_config:
        name = f"{model['provider']}:{model['model']}"
        resultados = resultados_por_modelo.get(name, []) or resultados_por_modelo.get(model['model'], [])
        if resultados:
            tiempo_total = sum(int(r.get('tiempo_ms') or 0) for r in resultados)
            tokens_total = sum(int(r.get('tokens_totales') or 0) for r in resultados)
            ranking.append((name, tiempo_total, tokens_total, model['provider']))
        else:
            ranking.append((name, 0, 0, model['provider']))

    ranking.sort(key=lambda item: (item[3] != 'ollama', item[1], item[2]))

    local_candidates = [item for item in ranking if item[3] == 'ollama']
    external_candidates = [item for item in ranking if item[3] == 'gemini']

    recommended_name = None
    if local_candidates:
        first_local = local_candidates[0]
        recommended_name = first_local[0]

    if recommended_name is None:
        recommended_name = ranking[0][0]

    content = f"""# Recomendación de Modelo para Deployment

## Análisis de Benchmark

Tras ejecutar el benchmark con casos seleccionados sobre políticas internas de Bridge SA, la decisión debe priorizar un modelo local coherente si cumple el umbral mínimo de calidad y robustez. En caso contrario, se puede valorar un modelo externo para casos más complejos.

## Criterios de decisión

- Calidad en preguntas de dominio, límites y ambigüedad.
- Latencia percibida por el usuario.
- Coste por token, especialmente en modelos Gemini, por lo que la respuesta debe ser lo más contenida posible.
- Sostenibilidad operativa y facilidad de despliegue.

## Ranking

1º {recommended_name}: candidato principal y preferido si ofrece un rendimiento suficiente y coherente con el uso de onboarding.
2º {external_candidates[0][0] if external_candidates else ranking[1][0] if len(ranking) > 1 else 'N/A'}: buena alternativa cuando se necesita mayor robustez en respuestas complejas o mayor capacidad de razonamiento.
3º {external_candidates[1][0] if len(external_candidates) > 1 else (local_candidates[1][0] if len(local_candidates) > 1 else ranking[2][0] if len(ranking) > 2 else 'N/A')}: opción secundaria si se busca un equilibrio entre calidad y coste, aunque normalmente será menos atractiva que la primera opción por el coste por token.

## Recomendación final

Se recomienda adoptar primero {recommended_name} si su rendimiento es coherente con los casos del benchmark. Si se necesita un nivel superior de calidad para tareas más complejas, el siguiente mejor candidato es {external_candidates[0][0] if external_candidates else 'otro modelo local'}.

## Nota de coste

Dado que los modelos Gemini suelen tener un coste por token más alto, conviene pedir en el prompt respuestas lo más contenidas posible y evitar respuestas redundantes. Esto mejora la relación calidad/coste sin perder claridad.
"""

    with open(output_dir / 'recomendacion.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Recomendación guardada en {output_dir / 'recomendacion.md'}")

   

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
                try:
                    create_matriz_decision(BENCHMARK_MODELS)
                    create_recomendacion(BENCHMARK_MODELS)
                    print("\n✓ → Benchmark completado exitosamente")
                    print(f"   - {len(resultados)} resultados procesados")
                    print(f"   - Archivos generados en:\n")
                    print("     → output/benchmark_resultados.csv")
                    print("     → entregables/matriz_decision.md")
                    print("     → entregables/recomendacion.md")
                except Exception as e:
                    print(f"⨉ → Error ejecutando benchmark: {e}")
                    import traceback
                    traceback.print_exc()
                
            else:
                print("⨉ No se obtuvieron resultados")
                
        except Exception as e:
            print(f"⨉ Error ejecutando el benchmark: {e}")
            return