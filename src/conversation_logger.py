"""Logs the raw API messages exchanged with Ollama for each agent call to a JSON file."""

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"


class ConversationLogger:
    def __init__(self, task: str):
        LOG_DIR.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        self.path = LOG_DIR / f"{stamp}.json"
        self.task = task
        self.entries = []
        self.rounds = []
        self._write()

    def log(self, agent: str, round_num: int, model: str, messages: list, response: str) -> None:
        self.entries.append(
            {
                "round": round_num,
                "agent": agent,
                "model": model,
                "messages": messages,
                "response": response,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._write()

    def log_round(self, round_num: int, code: str, reviewer_feedback: str) -> None:
        self.rounds.append(
            {
                "round": round_num,
                "code": code,
                "reviewer_feedback": reviewer_feedback,
            }
        )
        self._write()

    def _write(self) -> None:
        self.path.write_text(
            json.dumps({"task": self.task, "entries": self.entries, "rounds": self.rounds}, indent=2)
        )
