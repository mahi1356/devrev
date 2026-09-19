# Action Items

## Done

### Logging: surface code + reviewer feedback per iteration

Added a `rounds` array to `logs/<timestamp>.json` (via `ConversationLogger.log_round()`
in [src/conversation_logger.py](../src/conversation_logger.py), called from
[src/main_orthestrator.py](../src/main_orthestrator.py)) so each round's code and
the reviewer's feedback on it can be read at a glance, alongside the existing
full `entries` transcript. Applies to every run (direct and QuixBugs harness).
