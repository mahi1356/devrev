"""Reviewer agent: reviews the developer's code and suggests improvements or approves it."""

from ollama import Client

SYSTEM_PROMPT = """You are the reviewer agent. You review code written by the developer agent.
Point out bugs, risks, and improvements. If the code is acceptable, say APPROVED."""


class ReviewerAgent:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.client = Client()
        self.model = model

    def run(self, task: str, code: str, logger=None, round_num: int = 0) -> str:
        prompt = f"Task:\n{task}\n\nCode to review:\n{code}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat(model=self.model, messages=messages)
        content = response["message"]["content"]
        if logger:
            logger.log("reviewer", round_num, self.model, messages, content)
        return content
