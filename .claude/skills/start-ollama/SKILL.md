---
name: start-ollama
description: Start the local Ollama server used by this project's developer/reviewer agents (devrev). Use when the user asks to start, launch, run, or check Ollama, or when an agent run fails because Ollama isn't reachable at localhost:11434.
---

# Start Ollama server

This project's agents ([src/developer_agent.py](../../src/developer_agent.py), [src/reviewer_agent.py](../../src/reviewer_agent.py)) call a local Ollama server at `http://127.0.0.1:11434`. Ollama does not auto-start on this machine, so it must be started manually before running the agents.

## Steps

1. Check if it's already running:
   ```bash
   curl -s http://127.0.0.1:11434 || echo "not running"
   ```
   If it responds with "Ollama is running", stop here — nothing to do.

2. If not running, start it in the background and log output:
   ```bash
   nohup ollama serve > /tmp/ollama-serve.log 2>&1 &
   disown
   ```

3. Confirm it came up:
   ```bash
   sleep 2
   curl -s http://127.0.0.1:11434
   ```

4. Confirm the model this project uses is available:
   ```bash
   ollama list
   ```
   Expect `qwen2.5-coder:7b` in the list. If missing, pull it:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

## Notes

- `ollama` binary lives at `/usr/local/bin/ollama` on this machine (installed manually from ollama.com's macOS tarball, since Homebrew's cask requires macOS Sonoma+ and this machine runs Monterey 12.7.6).
- The server does not persist across reboots — it must be restarted each session unless a launchd agent is set up separately.
- Do not use `ollama serve` in the foreground in an agent context — it blocks; always background it with `nohup ... &` as above.
