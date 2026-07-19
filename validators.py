import unicodedata


MAX_INPUT_CHARS = 2_000
PATRONES_SOSPECHOSOS = (
    # Inyección / jailbreak
    "ignora instrucciones",
    "ignore previous",
    "olvida que eres",
    "no eres mas un asistente",
    "actua como",
    "disregard",
    "system:",
    "jailbreak",
    "olvida que",

    # Datos sensibles (salariales)
    "cuanto gana",
    "cuanto cobra",
    "sueldo",
    "salario",
    "nomina",
    "bonus",

    # Fuera de dominio
    "curso externo",
    "ejercicio",
    "programa formativo",
    "estoy estudiando",
    "soy participante de",
    "ayuda con mi tarea",
    "modulo"
)


def quita_acentos(texto:str) -> str:
    forma_nfd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in forma_nfd if unicodedata.category(c) != "Mn")



def validacion_input(mensaje: str) -> dict:
    mensaje_normalizado = quita_acentos(mensaje).lower().strip()
    errores = []
    if not mensaje_normalizado:
        errores.append("Mensaje inválido (falta): el mensaje no puede estar vacío")
    if len(mensaje_normalizado) > MAX_INPUT_CHARS:
        errores.append(f"Mensaje inválido (longitud): el mensaje no puede superar los {MAX_INPUT_CHARS} carácteres. Actualmente el mensaje tiene {len(mensaje_normalizado)} carácteres y se tiene que reducir del {(len(mensaje) - 2000)/ len(mensaje)}%.")
    for expresion in PATRONES_SOSPECHOSOS:
        if expresion in mensaje_normalizado:
            errores.append("Mensaje inválido (patrón no permitido): esta solicitud no puede ser procesada")
            break
    return {"ok": not errores, "errores": errores}

        
