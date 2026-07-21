class ConversationMemory:
    """
    Guarda el historial por empleado.
    """

    def __init__(self):
        self.memory = {}

    def add(self, employee_id, role, content):

        if employee_id not in self.memory:
            self.memory[employee_id] = []

        self.memory[employee_id].append({
            "role": role,
            "content": content,
        })

        # 4 turnos = 8 mensajes
        self.memory[employee_id] = self.memory[employee_id][-8:]

    def get(self, employee_id):
        return self.memory.get(employee_id, [])