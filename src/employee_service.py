import json


def load_employees(path: str) -> list:
    """Carga la lista de empleados."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_employee(employee_id: str, employees: list) -> dict | None:
    """Busca un empleado por su ID."""
    for employee in employees:
        if employee["id"] == employee_id:
            return employee

    return None