ROLES = ("employee", "manager", "hr", "executive")

# No real auth in this demo - switching "persona" simulates logging in as a
# different role, so retrieval-time enforcement is visible and testable.
PERSONAS = [
    {"id": "jordan", "name": "Jordan Blake", "title": "Software Engineer", "role": "employee"},
    {"id": "morgan", "name": "Morgan Reyes", "title": "Engineering Manager", "role": "manager"},
    {"id": "casey", "name": "Casey Whitfield", "title": "HR Business Partner", "role": "hr"},
    {"id": "taylor", "name": "Taylor Nakamura", "title": "VP of Finance", "role": "executive"},
]

_PERSONA_BY_ID = {p["id"]: p for p in PERSONAS}


def role_for_persona(persona_id: str) -> str | None:
    persona = _PERSONA_BY_ID.get(persona_id)
    return persona["role"] if persona else None
