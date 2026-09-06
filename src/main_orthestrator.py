"""Orchestrates the developer <-> reviewer loop until the reviewer approves or a round limit is hit."""

from conversation_logger import ConversationLogger
from developer_agent import DeveloperAgent
from reviewer_agent import ReviewerAgent

MAX_ROUNDS = 3


def run(task: str, code: str = "") -> str:
    developer = DeveloperAgent()
    reviewer = ReviewerAgent()
    logger = ConversationLogger(task)

    feedback = ""
    for round_num in range(1, MAX_ROUNDS + 1):
        code = developer.run(task, code=code, feedback=feedback, logger=logger, round_num=round_num)
        feedback = reviewer.run(task, code=code, logger=logger, round_num=round_num)
        print(f"--- Round {round_num} ---\nCode:\n{code}\n\nReview:\n{feedback}\n")

        if "APPROVED" in feedback:
            break

    print(f"Conversation logged to {logger.path}")
    return code


if __name__ == "__main__":
    run("Describe your task here")
