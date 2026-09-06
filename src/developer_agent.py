"""Developer agent: writes code and fixes bugs based on a task or reviewer feedback."""

from ollama import Client

SYSTEM_PROMPT = """You are the developer agent. You write code and fix bugs.
Given a task or feedback from a reviewer, produce the updated code."""


class DeveloperAgent:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.client = Client()
        self.model = model

    def run(self, task: str, code: str = "", feedback: str = "", logger=None, round_num: int = 0) -> str:
        prompt = f"Task:\n{task}\n\nCurrent code:\n{code}\n\nReviewer feedback:\n{feedback}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat(model=self.model, messages=messages)
        content = response["message"]["content"]
        if logger:
            logger.log("developer", round_num, self.model, messages, content)
        return content
