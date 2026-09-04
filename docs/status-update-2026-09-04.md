# Status Update — 2026-09-04

**Goal:** Set up the `devrev` project (two AI agents — developer & reviewer — that loop on code) to run for free, without an Anthropic API key.

## Environment setup
- Found the project needs `ANTHROPIC_API_KEY` by default (paid, not free).
- Compared free alternatives: Anthropic trial credit, Google Gemini free tier (pros/cons discussed — free but usage may train Google's models, rate limits, needs SDK rewrite), and **Ollama** (fully free, local, no key) — chose Ollama.
- Installed Ollama manually since Homebrew's cask requires macOS Sonoma+ and this machine runs **Monterey 12.7.6, Intel x86_64**: downloaded the official binary tarball directly, placed it in `/usr/local/bin` and `/usr/local/lib/ollama`, started `ollama serve` in the background.
- Pulled **`qwen2.5-coder:7b`** as the local model (CPU-only, no GPU — noted this limits speed and rules out real fine-tuning).

## Code changes
- Rewired [src/developer_agent.py](../src/developer_agent.py) and [src/reviewer_agent.py](../src/reviewer_agent.py) to call Ollama's local `Client().chat()` instead of the Anthropic SDK.
- Updated [requirements.txt](../requirements.txt) (`anthropic`→`ollama`).
- Removed `.env`, `.env.example`, and `load_dotenv()` from [src/main.py](../src/main.py) — no longer needed since Ollama requires no API key. Uninstalled `python-dotenv`.
- [src/main.py](../src/main.py)'s `run()` now accepts an optional starting `code` argument (needed to feed in existing buggy code rather than starting from scratch).
- Verified the full developer↔reviewer loop end-to-end on a test task — works, though noted the reviewer sometimes phrases approval inconsistently (e.g. "Approved" vs "APPROVED"), which affects the strict substring match that ends the loop early (flagged, not yet fixed).

## Skill
- Created a project skill at `.claude/skills/start-ollama/SKILL.md` to check/start the Ollama server and verify the model is present. Note: skills load at session start, so it wasn't invocable in the same session it was created — works on next session.

## Datasets for testing bugs
- Discussed open-source bug datasets: **QuixBugs**, SWE-bench, Defects4J, BugsInPy, BigVul/Devign — pros/cons for each.
- Added a **Datasets** section to [README.md](../README.md) documenting all five.
- Cloned **QuixBugs** into `tests/quixbugs/` (stripped its nested `.git`).

## Alternative LLM backends (discussed, not implemented)
- Explained the `claude` CLI (Claude Code itself) as a non-API way to call Claude via `claude -p "prompt" --output-format json`, using subscription auth instead of pay-per-token billing. Noted the JSON output still reports a `total_cost_usd` even under subscription — worth confirming with account settings before relying on it. Decided to keep Ollama as the primary backend.

## Model improvement research
- Discussed ways to improve the local model: prompt tuning, Modelfile customization, fine-tuning (LoRA vs full), RAG, bigger models.
- Saved this to [docs/improving-ollama.md](improving-ollama.md), including a dedicated section on the lowest-memory/token way to actually train (LoRA on a small 0.5B–1.5B model via Unsloth, small dataset, CPU caveat).

## QuixBugs wiring (main deliverable)
- Built [tests/run_quixbugs.py](../tests/run_quixbugs.py): feeds a buggy QuixBugs program through the developer/reviewer loop, extracts the fixed code from the agent's reply, temporarily swaps it into `python_programs/<name>.py`, runs QuixBugs' real pytest suite against it, then restores the original buggy file (`try/finally`).
- Hardened it after live debugging:
  - Added a **30s subprocess timeout** — discovered QuixBugs' own buggy programs can genuinely infinite-loop (e.g. `bitcount`'s bug `n ^= n - 1` never terminates for most inputs), so testing must not run unguarded.
  - Fixed `extract_code()` to return `None` (not raw prose) when the agent's final reply has no code fence — previously this corrupted the target `.py` file and crashed pytest collection (caught via a real failure on `flatten`).
- **Verified results:** `bitcount` → PASS (agent correctly changed `^=` to `&=`), `find_first_in_sorted` → PASS, `flatten` → fails cleanly now (agent's final reply lacked a code block — a real model limitation, not a script bug).

## Current state
Everything runs free and locally. Usage: `python tests/run_quixbugs.py <name>` for one program, or no args for all 40 in the dataset.
