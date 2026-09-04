# Improving the local Ollama model

Ways to make the local model (`qwen2.5-coder:7b`) better, in order of effort.

## 1. Better prompting / system prompt tuning
Easiest option, no training involved. Adjust the `SYSTEM_PROMPT` constants in
[src/developer_agent.py](../src/developer_agent.py) and
[src/reviewer_agent.py](../src/reviewer_agent.py) to be more specific about
style, constraints, and output format. Biggest improvement for the least effort.

## 2. Modelfile customization
Ollama lets you create a custom model variant with a fixed system prompt,
temperature, and parameters baked in, so you don't have to pass the system
prompt on every call:

```bash
ollama create mymodel -f Modelfile
```

Still no training involved — just packaging config around the existing model.

## 3. Fine-tuning
Actually retrain the model's weights on examples (e.g. good bug-fix diffs)
using a tool like Unsloth or Axolotl, then convert to GGUF and load into
Ollama. This is real "teaching" but needs a labeled dataset, a GPU, and
meaningfully more setup.

**Not practical on this machine** — CPU-only Intel Mac, no GPU, would be very slow.

## 4. RAG / retrieval
Instead of changing the model, feed it relevant context at runtime (e.g. the
codebase, past reviews, coding standards) so responses are better-informed
without touching weights. Moderate effort, no GPU needed.

## 5. Swap to a bigger/better local model
Not "teaching," but often the highest-leverage move: try `qwen2.5-coder:14b`
or `32b` instead of `7b` if the machine's RAM allows. Better answers for free,
zero training.

## Recommendation for this machine
Since this is a CPU-only Intel Mac with no GPU, real fine-tuning isn't
practical. Start with Modelfile customization + a bigger model if RAM allows.

## Lowest-memory/token way to actually train

If you want real weight training (not just prompting/RAG) while keeping
memory and token usage as low as possible:

**LoRA fine-tune a small model (`qwen2.5-coder:0.5b` or `1.5b`) with Unsloth**
- LoRA only trains small adapter weights (a few % of the model), not the
  full model — needs ~4-8GB RAM instead of 40GB+ for a full fine-tune.
- Use a small model (0.5B-1.5B params) — dramatically less memory than the
  7B model currently in use.
- Keep the training dataset small (dozens to low hundreds of examples, e.g.
  QuixBugs fixes) — fewer tokens processed = faster and cheaper.
- After training, merge the adapter and convert to GGUF to load into Ollama.

**Caveat:** even "cheap" LoRA is still slow on CPU-only hardware (hours, not
minutes, for even a small run) since there's no GPU acceleration. It'll work,
just not fast.

**If low memory AND low token cost matters more than actual weight training**,
skip training entirely — Modelfile customization (zero memory/token cost) or
RAG (no training, just runtime context) are the cheapest options above. They
won't make the model fundamentally smarter but improve output quality for free.
