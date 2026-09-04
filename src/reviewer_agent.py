"""Reviewer agent: reviews the developer's code and suggests improvements or approves it."""

from ollama import Client

SYSTEM_PROMPT = """You are the reviewer agent. You review code written by the developer agent.
Point out bugs, risks, and improvements. If the code is acceptable, say APPROVED."""


class ReviewerAgent:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.client = Client()
        self.model = model

    def run(self, task: str, code: str) -> str:
        prompt = f"Task:\n{task}\n\nCode to review:\n{code}"
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response["message"]["content"]
