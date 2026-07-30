from ollama import Client


class LLMClient:

    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "llama3.2:3b"

    def generate(self, prompt: str) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0.2,
            },
        )

        return response["message"]["content"]