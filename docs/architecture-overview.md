# Architecture Overview

`devrev` is a small two-agent code-fixing loop that runs entirely locally via
Ollama (no API key/billing needed), tested against the QuixBugs bug-fixing
benchmark.

## The files, and how they connect

### Agent pair (`src/`)

- **[developer_agent.py](../src/developer_agent.py)** — `DeveloperAgent` calls
  a local Ollama model (`qwen2.5-coder:7b`) with a system prompt telling it to
  write/fix code given a task, current code, and prior reviewer feedback.
- **[reviewer_agent.py](../src/reviewer_agent.py)** — `ReviewerAgent` calls the
  same model with a different system prompt: critique the developer's code, or
  reply `APPROVED` if it's fine.
- **[main.py](../src/main.py)** — the orchestrator. `run(task, code)`
  alternates developer → reviewer up to `MAX_ROUNDS = 3`, feeding each
  reviewer critique back into the next developer call, and stops early if
  `"APPROVED"` appears in the feedback.

### Dependencies / config

- **[requirements.txt](../requirements.txt)** — just `ollama` (the Python
  client for the local server).
- **`.claude/skills/start-ollama/SKILL.md`** — a Claude Code skill that
  checks/starts the local Ollama server (`127.0.0.1:11434`) and verifies
  `qwen2.5-coder:7b` is pulled, since Ollama doesn't auto-start on this
  machine.

### Test harness (`tests/`)

- **[run_quixbugs.py](../tests/run_quixbugs.py)** — bridges the agent loop to
  a real benchmark: for each QuixBugs program, it feeds the buggy source into
  `main.run()` as a "fix this bug" task, regex-extracts the code block from
  the agent's final reply, temporarily overwrites the real QuixBugs source
  file with the fix, runs QuixBugs' actual pytest suite against it (30s
  timeout, since unfixed bugs can infinite-loop), records pass/fail, then
  restores the original buggy file in a `finally` block. Runnable for a
  single program or all 40.
- **`tests/quixbugs/`** — the vendored QuixBugs dataset itself (40 classic
  algorithms in Python + Java, each with a known one-line bug, correct
  reference versions, and pytest test cases). This is pure external fixture
  data that `run_quixbugs.py` reads/writes into — not code you'd modify.

### Docs

- **[README.md](../README.md)** — project overview, setup instructions, and a
  comparison table of bug datasets (QuixBugs vs SWE-bench vs Defects4J vs
  BugsInPy vs BigVul/Devign), explaining why QuixBugs was chosen.
- **[docs/improving-ollama.md](improving-ollama.md)** — a menu of options
  (prompt tuning → Modelfile → fine-tuning → RAG → bigger model) for
  improving the local model's output quality, with a recommendation tailored
  to this machine (CPU-only Intel Mac, no GPU).
- **[docs/status-update-2026-09-04.md](status-update-2026-09-04.md)** — a dev
  log of a past session: migrating off the Anthropic API to Ollama, building
  the QuixBugs harness, and known issues (e.g. reviewer inconsistently says
  "Approved" vs "APPROVED", which affects the strict substring check in
  `main.py`'s loop-exit condition).

## The data flow

```
run_quixbugs.py
  -> main.run()
       -> alternates DeveloperAgent / ReviewerAgent (both hit local Ollama)
  -> extracted fix swapped into tests/quixbugs/python_programs/<name>.py
  -> QuixBugs' own pytest suite verifies it
  -> original buggy file restored
```

## Known issue

The strict substring match `"APPROVED" in feedback` in
[main.py:19](../src/main.py#L19) can miss approvals when the model writes
"Approved" instead of "APPROVED" — noted in the status update but not yet
fixed.
