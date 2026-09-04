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
  developer_agent.py   # writes/fixes code
  reviewer_agent.py    # reviews and suggests changes
  main.py               # orchestrates the developer <-> reviewer loop
tests/
```
