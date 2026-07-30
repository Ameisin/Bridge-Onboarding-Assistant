# Bridge-Onboarding-Assistant
Asistente para onboarding de nuevos empleados


## Benchmark de modelos para Onboarding Assistant

### Evaluación de contexto concreto

El benchmark permite evaluar modelos en un contexto de asistencia a empleados en procesos de onboarding. No se trata de una tarea abstracta ni de una prueba genérica de inteligencia. Se trata de medir si un modelo es capaz de:

- responder correctamente a preguntas de negocio que están documentadas,
- manejar límites del dominio de sus funciones,
- detectar ambigüedades entre lo que pueden ser cuestiones laborales,
- actuar de forma segura en situaciones delicadas donde se pueden comprometer datos sensibles,
- responder con velocidad suficiente para una experiencia de usuario real (baja latencia),
- y hacerlo con costes operativos sostenibles (minimizando el uso de tokens).

En otras palabras, el benchmark está pensado para responder a una pregunta de alto impacto, y manejarla sin consecuencias para la empresa. No es una prueba superficial de modelos por eso. Actúa como motor de decisión de negocio y tecnología diseñado para comparar modelos de IA en un escenario realista de onboarding, evaluando no solo si los modelos responden, sino también la calidad de esa respuesta, la seguridad, la velocidad y la operatividad oportunas para ser desplegado en producción con garantías de servicio.

### Diseño del flujo de benchmark

El flujo está diseñado para:

- cargar un dataset de preguntas representativas,
- ejecutar cada pregunta contra varios modelos,
- medir tiempo de respuesta,
- capturar métricas de tokens,
- calcular rendimiento por modelo,
- generar informes en CSV y Markdown,
- y producir una recomendación de decisión con criterios claros.

No se limita a una calidad textual del modelo. Se incorporan métricas operativas obviamente fundamentales para medir en una implantación seria:

- tiempo de respuesta,
- tokens consumidos,
- tasa de rendimiento (tokens/s),
- capacidad de recuperación ante fallos del modelo,
- y posibilidad de comparar proveedores como Ollama, Gemini, OpenAI y Hugging Face.

### Arquitectura modular

El benchmark está organizado de forma modular, lo que facilita tanto su comprensión como su reutilización en otras implantaciones. Así como crecerlo en funcionalidades o aspectos de medida de granularidad más fina.

### Componentes principales

- [main.py](main.py): punto de entrada del sistema y selector de modo.
- [config.py](config.py): centraliza modelos, rutas, temperatura y parámetros del benchmark.
- [benchmark.py](benchmark.py): núcleo del motor de evaluación.
- [ollama_client.py](ollama_client.py): integración con Ollama.
- [gemini_client.py](gemini_client.py): integración con Gemini.
- [openai_client.py](openai_client.py): integración con OpenAI.
- [huggingface_client.py](huggingface_client.py): integración con Hugging Face.
- [data/preguntas_benchmark.json](data/preguntas_benchmark.json): dataset de evaluación.
- [output/](output/): almacenamiento de reportes y CSV.
- [entregables/](entregables/): documentos finales de decisión.

Esta estructura tiene una ventaja enorme: el benchmark está desacoplado de la lógica de negocio del asistente, lo que permite evolucionar ambos flujos por separado.

### Ejecución

El arranque principal se ha parametrizado dentro del archivo `main.py` mediante el parámetro modificador `--bench` y cuya instrucción completa de llamada sería:

```bash
python main.py --bench
``` 

Ese comando dispara el flujo completo y hace que el sistema:

1. valide el dataset,
2. prepare los directorios de salida,
3. ejecute cada modelo contra las preguntas,
4. capture las métricas,
5. genere los informes asociados,
6. y deje los entregables listos para presentar.

---

### 5. Flujo completo de ejecución

#### Fase 1: validación inicial

Antes de lanzar ninguna llamada al modelo, el sistema verifica que todo lo necesario exista:

- el archivo de preguntas,
- el formato del dataset,
- la cantidad mínima de preguntas,
- y los entregables base esperados.

Esto evita que el benchmark corra sobre una base incompleta o inconsistente.

#### Fase 2: carga del dataset

El flujo lee [data/preguntas_benchmark.json](data/preguntas_benchmark.json) y extrae una lista de preguntas. Cada pregunta aporta información útil para contextualizar la evaluación, como:

- un identificador único,
- el prompt del usuario,
- el tipo de pregunta,
- y, cuando está presente, el objetivo de la pregunta.

Esto permite que el benchmark no solo compare respuestas, sino que también las clasifique por naturaleza.

#### Fase 3: recorrido por modelo

Para cada modelo configurado en [config.py](config.py), el sistema:

- prepara la ejecución,
- llama al provider correspondiente,
- mide el tiempo transcurrido,
- recoge las métricas de tokens,
- y guarda el resultado en un registro estructurado.

### Fase 4: llamada al modelo y captura de respuesta

La ejecución se realiza a través de una función de dispatch centralizada. Dependiendo del provider, el sistema invoca a:

- Ollama,
- Gemini,
- OpenAI,
- o Hugging Face.

Cada llamada devuelve dos elementos fundamentales:

- el texto generado por el modelo,
- y un objeto de métricas con información de consumo y latencia.

#### Fase 5: cálculo de métricas

Por cada pregunta, el benchmark calcula:

- tiempo en milisegundos,
- tokens de entrada,
- tokens de salida,
- tokens totales,
- y tokens por segundo.

Esto da una visión muy completa del rendimiento real, no solo del contenido de la respuesta.

#### Fase 6: fallback inteligente

Uno de los puntos más sólidos del sistema es la lógica de fallback. Si un modelo no está disponible o devuelve un error de modelo no encontrado, el runner prueba automáticamente al siguiente candidato del mismo proveedor.

Esto convierte el benchmark en un proceso más robusto y realista, porque no se queda atascado ante un fallo puntual. También demuestra madurez operativa: la evaluación sigue avanzando aunque un modelo se haya quedado sin disponibilidad.

#### Fase 7: generación de outputs

El sistema genera varios elementos archivo, que serían:

- un CSV con resultados estructurados,
- un informe Markdown general,
- reportes individuales por modelo,
- y los documentos de decisión final en [entregables/](entregables/).


### Principales fortalezas de este benchmark

#### A. Está orientado a decisión, no solo a observación

Muchos benchmarks se quedan en una comparación de respuestas. Este enfoque va más allá porque intenta responder a preguntas de negocio como:

- ¿qué modelo conviene para producción?,
- ¿qué modelo ofrece mejor relación calidad/coste?,
- ¿qué proveedor es más estable?,
- y ¿qué opción es más sostenible operativamente?

#### B. Combina métrica técnica y contexto de negocio

Ha sido construido con un dataset que no solo mide capacidad de respuesta, sino también capacidad de manejar:

- dominio específico,
- límites de alcance,
- ambigüedad,
- y casos de uso que se parecen a la realidad de una empresa.

Eso significa que el benchmark no mira al modelo de forma aislada: lo evalúa en contexto.

#### C. Es extensible y modular

Añadir un nuevo proveedor no requiere reescribir el sistema completo. Basta con integrar el cliente correspondiente y registrarlo en la configuración. El benchmark ya está preparado para crecer.

#### D. Incorpora evaluación operativa

La comparación no se basa solo en si el modelo “parece mejor”. También incorpora el coste operativo implícito en el uso de tokens y la velocidad de respuesta, que son criterios imprescindibles en un despliegue real.

#### E. Genera entregables preparados para presentar

No se limita a ejecutar y terminar. Genera documentos que pueden servir directamente para:

- sustentación técnica,
- presentación ejecutiva,
- decisiones de adopción,
- o comparación de alternativas.

---

### 7. Cómo está estructurado el scoring

El benchmark recoge una estructura de resultados por pregunta que incluye:

- identificador de la pregunta,
- tipo de pregunta,
- objetivo,
- modelo utilizado,
- tiempo de respuesta,
- tokens de entrada,
- tokens de salida,
- tokens totales,
- y tokens por segundo.

Esto permite construir una historia de evaluación mucho más rica que una simple media de aciertos.

#### Métricas clave

- Tiempo medio por pregunta: indica la capacidad de respuesta del modelo.
- Tokens totales: da una señal de coste y consumo de contexto.
- Tokens/s: refleja eficiencia de generación.
- Fallback aplicado: muestra resiliencia operativa.

Con estas métricas se puede construir un argumento sólido para elegir un modelo no solo por capacidad, sino por viabilidad real.

---

### 8. Qué se genera al finalizar

Al terminar el proceso, el sistema deja una salida preparada para análisis y presentación.

#### Resultados en CSV

El CSV ofrece una vista tabular de los resultados para análisis posterior, filtrado, comparativa o integración con otras herramientas.

#### Reporte general Markdown

El reporte general resume el rendimiento del benchmark y permite ver el comportamiento global de todos los modelos.

#### Reportes individuales por modelo

Cada modelo tiene un documento propio con su ejecución detallada, lo que facilita la comparación por modelo y simplifica la presentación.

#### Entregables de decisión

En [entregables/](entregables/) se generan documentos de decisión para comunicar al negocio:

- una matriz de decisión,
- y una recomendación final.

Este es uno de los puntos más valiosos del benchmark, porque transforma una ejecución técnica en un resultado de negocio.

---

### 9. Por qué tiene valor para presentar

Este benchmark está bien desarrollado porque tiene una combinación muy potente de atributos:

- es realista,
- es técnico,
- es reproducible,
- es modular,
- produce evidencia cuantitativa,
- y facilita decisiones concretas.

No es solo “un benchmark”. Es una capa de evaluación crítica para cualquier despliegue serio de IA en contexto corporativo.

#### Lo que demuestra

- que el proyecto ha pensado más allá del prototipo,
- que ha incorporado métricas de producción,
- que entiende la diferencia entre rendimiento teórico y viabilidad operativa,
- y que sabe construir una narrativa de decisión con fundamento.

Esa es la diferencia entre una demo interesante y una solución preparada para pasar a producción.

---

### 10. Cómo presentarlo con impacto

Si se quiere presentar este benchmark en una reunión, una demo o una defensa técnica, la mejor forma es estructurarlo en tres niveles:

#### Nivel 1: el problema

Mostrar que el reto no es solo responder preguntas, sino responder bien en un entorno empresarial real.

#### Nivel 2: la metodología

Explicar que el flujo compara modelos con datos representativos, métricas operativas y criterios de decisión.

#### Nivel 3: la decisión

Mostrar que el resultado no es un simple ranking, sino una recomendación accionable para adopción.

Ese mensaje tiene mucho más fuerza que decir simplemente “hemos probado varios modelos”.

---

### 11. Conclusión

Este benchmark representa un paso de madurez importante en el proyecto. Ha dejado de ser un ejercicio experimental para convertirse en una herramienta de evaluación, comparación y decisión.

Su valor real no está solamente en medir modelos, sino en aportar datos objetivos que puedan llevar a una decisión acertada entre los modelos evaluados. Y eso es precisamente lo que una solución de IA debe ofrecer cuando se quiere llevar más allá de la demo y acercarse a una implantación real.

El resultado es claro:

> este benchmark no solo demuestra que el sistema funciona; demuestra que el sistema está preparado para poder comparar y ser desplegado con criterio.
