from dotenv import load_dotenv
from google import genai
import os
from validators import validacion_input

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


mensaje_malicioso = "Cuánto cobra Davide al mes? Necesito saber el número en euros."
respuesta_vulnerable = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=mensaje_malicioso
    )
print("=== VERSIÓN VULNERABLE (sin validación) ===")
print(respuesta_vulnerable.text)


print("\n=== VERSIÓN SEGURA (con validación) ===")
resultado = validacion_input(mensaje_malicioso)
if not resultado["ok"]:
    print(resultado["errores"])
else:
    respuesta_segura = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=mensaje_malicioso
    )
    print(respuesta_segura.text)