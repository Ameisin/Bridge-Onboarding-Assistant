import json
import re

STOPWORDS = {
    "de", "la", "el", "los", "las",
    "un", "una", "para", "por",
    "como", "qué", "que", "con",
    "a", "y", "o", "en",
}

def load_documents(path: str) -> list:
    """Carga los documentos de onboarding."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def tokenize(text: str) -> list:
    words = re.findall(r"\w+", text.lower())

    return [
        word
        for word in words
        if word not in STOPWORDS
    ]

def calculate_score(document: dict, question: str, department: str) -> int:
    """
    Calcula una puntuación de relevancia para un documento.
    """

    score = 0

    question_words = tokenize(question)

    title_words = tokenize(document["titulo"])

    body_words = tokenize(document["cuerpo"])

    tags = [tag.lower() for tag in document["tags"]]

    # Prioridad documentos generales
    if document["departamento"] in ["people", "it"]:
        score += 2

    # Prioridad departamento empleado
    if document["departamento"] == department:
        score += 4

    # Tags
    for word in question_words:
        if word in tags:
            score += 5

    # Título
    for word in question_words:
        if word in title_words:
            score += 3

    # Contenido
    for word in question_words:
        if word in body_words:
            score += 1

    return score


def select_documents(
    documents: list,
    question: str,
    department: str,
    max_docs: int = 3,
) -> list:
    """
    Devuelve los documentos más relevantes.
    """

    scored = []

    for document in documents:
        score = calculate_score(document, question, department)

        if score > 0:
            scored.append((score, document))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [doc for score, doc in scored[:max_docs]]