"""Developer agent: writes code and fixes bugs based on a task or reviewer feedback."""

from ollama import Client

SYSTEM_PROMPT = """You are the developer agent. You write code and fix bugs.
Given a task or feedback from a reviewer, produce the updated code."""


class DeveloperAgent:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.client = Client()
        self.model = model

    def run(self, task: str, code: str = "", feedback: str = "") -> str:
        prompt = f"Task:\n{task}\n\nCurrent code:\n{code}\n\nReviewer feedback:\n{feedback}"
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response["message"]["content"]
