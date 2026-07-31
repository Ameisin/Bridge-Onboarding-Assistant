# Matriz de Decisión del Modelo

## Objetivo

Esta matriz recoge la comparación de los modelos probados para el asistente de onboarding de Bridge SA. La decisión final prioriza calidad suficiente en tareas de dominio, seguridad frente a ataques, capacidad para responder de forma estructurada y viabilidad operativa para el proyecto.

## Modelos evaluados

Se han comparado cinco opciones:

- `ollama:qwen3.5:9b`.
- `gemini:gemini-3.5-flash-lite`.
- `ollama:gpt-oss-safeguard:20b`.
- `gemini:gemini-3.5-flash`.
- `huggingface:openai/gpt-oss-20b`.

## Criterios de evaluación

Los criterios usados para decidir son:

1. Calidad en preguntas de onboarding, límites, ambigüedad y salida JSON.
2. Seguridad frente a inyección, datos sensibles y fuera de dominio.
3. Latencia percibida por el usuario.
4. Coste operativo y sostenibilidad.
5. Facilidad de despliegue e integración.

## Resumen de resultados

| Modelo | Tipo | Rendimiento observado | Observación relevante |
|---|---|---:|---|
| `ollama:qwen3.5:9b` | Local/privado | Correcto, pero con latencias altas y salidas largas. | Funciona, pero es más pesado y menos eficiente que `flash-lite`. Aunque sería posible quizá si se le parametrizasen adecuadamente los tokens de salida.|
| `gemini:gemini-3.5-flash-lite` | API externa | Muy buen equilibrio entre velocidad y calidad | Es el mejor candidato técnico entre los modelos realmente disponibles. |
| `ollama:gpt-oss-safeguard:20b` | API externa| Más lento que `flash-lite` y menos competitivo | Útil como referencia, pero no destaca frente a la alternativa externa de Google. |
| `gemini:gemini-3.5-flash` | API externa | No se selecciona para despliegue | Se descarta por alta demanda habitual, aunque el rendimiento pueda ser bueno. |
| `huggingface:openai/gpt-oss-20b` | API externa | Rendimiento aceptable en los casos completados | Los casos 10, 11 y 12 fallaron por falta de créditos, así que no deben penalizarse, pero tampoco es completa la evaluación. |

## Lectura del benchmark

En el benchmark, `gemini-3.5-flash-lite` responde de forma consistente en tareas de dominio, límites, ambigüedad y checklist JSON, además de hacerlo con tiempos significativamente más bajos que `qwen3.5:9b` y `gpt-oss-safeguard:20b`.  
`qwen3.5:9b` ofrece una opción local válida, pero en este conjunto de pruebas queda por detrás en eficiencia y no aporta una ventaja suficiente para compensar la diferencia. Esto como modelo `as is`, al menos sin entrar en parametrización que podría optimizar sensiblemente la salida (además del proceso de razonamiento previo a respuesta - _no registrado en la muestra_).  
`openai/gpt-oss-20b` puede evaluarse por completo, porque esos fallos (preguntas 10, 11 y 12) se deben a agotamiento de créditos y no a una incapacidad real del modelo en esos casos.

## Decisión

La opción recomendada para el proyecto es `gemini:gemini-3.5-flash-lite` como modelo principal.  
Se descarta `gemini:gemini-3.5-flash` por su alta demanda habitual y no por su calidad.  
Como plan alternativo, `ollama:qwen3.5:9b` puede reservarse si el equipo prioriza despliegue local y control operativo por encima de la mejor relación calidad/latencia.

## Conclusión operativa

La decisión favorece el modelo con mejor equilibrio entre calidad, velocidad y robustez real en el benchmark.  
Para este caso, ese equilibrio lo ofrece `gemini:gemini-3.5-flash-lite`, igualmente dejando claro que no se debe penalizar injustamente a `openai/gpt-oss-20b` por los errores derivados de falta de créditos en las últimas 3 preguntas del test.
