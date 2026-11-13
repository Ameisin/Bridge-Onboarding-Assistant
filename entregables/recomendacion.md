# Recomendación de Modelo para Deployment

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

`gemini:gemini-3.5-flash` queda descartado para la recomendación final por alta demanda habitual observada en este y anteriores benchmark.  
La exclusión es operativa, no técnica: no se descarta por rendimiento, sino por disponibilidad esperada en escenarios reales dada su alta demanda en detrimento de su nivel de servicio.

## Cierre

La recomendación final es usar `gemini:gemini-3.5-flash-lite` como modelo elegido para la entrega.  
Si en una segunda fase el equipo prioriza soberanía y control, `qwen3.5:9b` sería el siguiente candidato a evaluar en despliegue propio.
