# Recomendación de Modelo para Deployment

## Caso de uso

El Employee Onboarding Assistant acompaña a los empleados nuevos de Bridge SA en sus primeros días. Responde dudas con la documentación interna, genera el checklist del día en JSON y se adapta al perfil (dev junior, comercial, remoto UE) y al día de onboarding (1–5).

No responde sobre salarios ni sobre datos de otros empleados, no atiende a participantes externos de los programas formativos y no inventa políticas que no estén documentadas. Las consultas que no pasan la validación se rechazan sin llamar al modelo (fail-closed, ver `ROBUSTEZ.md`).

## Contexto

El asistente de onboarding de Bridge SA necesita un modelo capaz de responder preguntas de dominio, rechazar consultas sensibles o fuera de alcance, y generar salidas estructuradas como checklists JSON. La decisión debe priorizar una combinación de calidad funcional, velocidad de respuesta y fiabilidad operativa.

## Resultado del benchmark

El benchmark muestra que `gemini:gemini-3.5-flash-lite` ofrece la mejor combinación de resultados entre los modelos probados.  
Responde con buena calidad en casos de dominio, ambigüedad, seguridad y salida estructurada, y además lo hace con menor latencia que `qwen3.5:9b` y `gpt-oss-safeguard:20b`.

`ollama:qwen3.5:9b` sigue siendo una alternativa sólida si se valora más el control local que la velocidad o la consistencia general.  
`ollama:gpt-oss-safeguard:20b` no supera a `flash-lite` en este benchmark y queda como opción secundaria.  
`huggingface:openai/gpt-oss-20b` no debe penalizarse por el resultado obtenido en las preguntas 10, 11 y 12 porque esos fallos se explican por falta de créditos del modelo durante la ejecución, aunque tampoco alcanza el nivel presentado.

## Recomendación principal

Se recomienda desplegar `gemini:gemini-3.5-flash-lite` como modelo principal del asistente.  
Es la opción más equilibrada para un producto de onboarding: suficientemente robusta, rápida y adecuada para los casos de uso más importantes del proyecto.

## Alternativa

Si el proyecto necesita minimizar dependencia externa, la mejor alternativa es `ollama:qwen3.5:9b`.  
Esa opción aporta mayor control de despliegue, aunque en este benchmark no supera a `flash-lite` en calidad práctica ni en eficiencia global como modelo.

## Exclusiones

`gemini:gemini-3.5-flash` queda descartado para la recomendación final porque en esta ejecución no devolvió ninguna respuesta (0/12): errores 503 por alta demanda y 429 por el límite de la cuota gratuita (5 peticiones/minuto).  
La exclusión es operativa, no técnica: no se pudo medir su calidad, así que no se descarta por rendimiento, sino por disponibilidad.

## Trade-off principal

Ganamos latencia y concisión: `gemini-3.5-flash-lite` responde en 0,9 s de media con unos 124 tokens de salida, y con la mejor fidelidad del benchmark (2,92/3, empatado con `qwen3.5:9b`).  
Perdemos control: es una API externa, así que las preguntas de los empleados salen a Google, y dependemos de la cuota y la disponibilidad del proveedor. La alternativa local (`qwen3.5:9b`) da control total, pero tarda unos 32 s por respuesta y genera 11 veces más tokens de salida.

## ¿Qué pasaría si duplicáramos el tráfico?

- **Tokens:** el consumo crece de forma lineal con el volumen. Con las medias del benchmark, 1.000 consultas con `gemini-3.5-flash-lite` son unos 0,33 M tokens; con el doble de tráfico, unos 0,66 M. Con `qwen3.5:9b` serían 1,6 M y 3,2 M, porque cada respuesta es unas 5 veces más larga en tokens totales.
- **El prompt real pesa más que el del benchmark:** el chat de la aplicación envía unos 500 tokens de entrada sin historial y unos 800 con historial (3 documentos + historial), frente a unos 210 en el benchmark. Con el doble de tráfico, lo que mantiene el coste bajo control son los límites de contexto (máximo 3 documentos, historial acotado).
- **El primer cuello de botella es la cuota, no el coste:** en este mismo benchmark `gemini-3.5-flash` devolvió 429 con 5 peticiones por minuto y Hugging Face se quedó sin créditos (402). Con el doble de usuarios haría falta un plan de pago con límites de peticiones adecuados, reintentos con espera progresiva y un modelo de respaldo.
- **Los modelos locales no escalan gratis:** a 21–32 s por respuesta en nuestro hardware, duplicar los usuarios simultáneos duplica la cola de espera, salvo que se añada más capacidad de GPU.
- **Lo que ya ayuda:** el validador rechaza las consultas inválidas sin llamar al modelo, así que no consumen tokens. Además, se podrían cachear las respuestas a las FAQ más frecuentes.

## Riesgo o condición

- No usaríamos este modelo si la política de datos de Bridge SA no permite enviar consultas de empleados a un proveedor externo. En ese caso, la opción es `qwen3.5:9b` en despliegue propio.
- Antes de desplegar validaríamos tres cosas:
  1. Repetir el benchmark con `gemini-3.5-flash` cuando haya cuota, para cerrar la comparación entre los dos modelos Gemini.
  2. Que el checklist cumpla el esquema JSON del enunciado: en el benchmark ningún modelo lo siguió sin que el prompt lo exigiera. En la aplicación, comprobar la salida con un parser JSON antes de mostrarla.
  3. Que la cuota de la API de Gemini cubra el tráfico esperado. El asistente ya usa `gemini-3.5-flash-lite` en `src/llm_client.py`.

## Cierre

La recomendación final es usar `gemini:gemini-3.5-flash-lite` como modelo elegido para la entrega.  
Si en una segunda fase el equipo prioriza soberanía y control, `qwen3.5:9b` sería el siguiente candidato a evaluar en despliegue propio.
