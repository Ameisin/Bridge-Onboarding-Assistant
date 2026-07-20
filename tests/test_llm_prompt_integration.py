import config
from main import build_llm_payload, infer_profile


def test_build_llm_payload_uses_system_prompt_and_profile():
    payload = build_llm_payload(
        "¿Cómo accedo a GitHub y al repositorio del equipo?",
        {"department": "engineering", "department_label": "Engineering"},
        [{"id": "doc-1", "titulo": "Acceso a GitHub", "cuerpo": "Activa 2FA y solicita membresía."}],
        profile_key="dev_junior",
    )

    assert payload["system_prompt"] == config.SYSTEM_PROMPT
    assert payload["profile_role"] == config.PERFILES["dev_junior"]["rol"]
    assert "Engineering" in payload["user_prompt"]
    assert "GitHub" in payload["user_prompt"]


def test_infer_profile_detects_commercial_profile():
    assert infer_profile("Tengo una duda sobre ventas y clientes") == "comercial"
