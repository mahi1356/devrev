# devrev

Two AI agents working together on code:

- **developer** — writes code and fixes bugs
- **reviewer** — reviews the developer's changes and suggests improvements

## Setup

Agents run locally via [Ollama](https://ollama.com) — no API key needed.

```bash
# install Ollama, then pull the model this project uses
ollama pull qwen2.5-coder:7b
ollama serve  # keep running in another terminal

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Datasets

Open-source datasets of real/known bugs, useful for feeding tasks through the developer/reviewer loop:

| Dataset | What it is | Best for |
|---|---|---|
| **[QuixBugs](https://github.com/jkoppel/QuixBugs)** (used in this project) | 40 small classic algorithm bugs, Python + Java, one-line fixes | Quick smoke-testing an agent |
| **[SWE-bench](https://github.com/princeton-nlp/SWE-bench)** | Real GitHub issues + fixes + tests, from popular Python repos | End-to-end agent bug-fixing eval |
| **[Defects4J](https://github.com/rjust/defects4j)** | Real bugs from Java open-source projects, isolated + reproducible | Java-specific, well-established in research |
| **[BugsInPy](https://github.com/soarsmu/BugsInPy)** | Real bugs from popular Python projects (like Defects4J but Python) | Smaller, simpler bugs than SWE-bench |
| **[BigVul](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset) / [Devign](https://sites.google.com/view/devign)** | Security vulnerabilities with labeled diffs (C/C++) | Security-focused bug detection |

This project uses **QuixBugs** — see `tests/quixbugs/`.

## Layout

```
src/
  developer_agent.py       # writes/fixes code
  reviewer_agent.py        # reviews and suggests changes
  main_orthestrator.py     # orchestrates the developer <-> reviewer loop
  conversation_logger.py   # logs each agent's API messages to logs/<timestamp>.json
tests/
  run_quixbugs-test-harness.py   # runs a QuixBugs bug (or all 40) through the loop and checks the fix
  quixbugs/                      # the QuixBugs dataset
```

## Running

Make sure `ollama serve` is running and the venv is active (see Setup), then:

| Command | What it runs | Use it for |
|---|---|---|
| `python3 src/main_orthestrator.py` | The developer/reviewer loop once, on the placeholder task hardcoded in the file, with no starting code. No correctness check. | Sanity-checking the agents + Ollama are wired up. |
| `python3 tests/run_quixbugs-test-harness.py bitcount` | Feeds one real buggy QuixBugs program through the loop, extracts the fix, and runs QuixBugs' own pytest suite against it (30s timeout), then restores the original file. | Testing the agents on one specific known bug, with a real pass/fail verdict. |
| `python3 tests/run_quixbugs-test-harness.py` | Same as above for **all 40** programs in `tests/quixbugs/python_programs/`, reporting an aggregate `N/40 passed`. | Full benchmark run across the dataset. |

Every `run()` call writes a full transcript (each agent's messages and responses, per round) to `logs/<timestamp>.json`.
