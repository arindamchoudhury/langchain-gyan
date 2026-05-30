---
name: lc-foundations-getting-set-up
description: Setup guide for LangChain Academy foundations course — prerequisites, installation, API keys, verification, Ollama local setup, troubleshooting
---

# Getting Set Up

> **Source:** [academy.langchain.com — Getting Set Up (Text)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python/texts/71234844-getting-set-up-text) · [README.md](https://github.com/langchain-ai/lca-lc-foundations/blob/main/README.md)
> **Added:** 2026-05-29 · **Updated:** 2026-05-30
> **Tags:** setup, uv, pip, conda, python, jupyter, langsmith, api-keys, openai, tavily, deepseek, ollama
> **Type:** documentation

> 📌 **Version note (updated 2026-05-30):**
> `pyproject.toml` and `requirements.txt` bumped to May 2026 latest: langchain 1.3.2, langchain-core 1.4.0, langchain-openai 1.2.2, langchain-anthropic 1.4.4, langchain-google-genai 4.2.4, langgraph 1.2.2, langgraph-cli 0.4.27, langchain-mcp-adapters 0.2.2.
> `environment.yml` added for conda users, pinned to Python 3.13 — **Python 3.14 is not yet supported** ([issue #34441](https://github.com/langchain-ai/langchain/issues/34441)).
> Course uses `gpt-5-nano`. `gpt-5.4-nano` (March 2026, $0.20/1M input) is the newer drop-in replacement.

## Summary

Environment setup guide for the "Foundation: Introduction to LangChain - Python" course. Covers cloning the repo, configuring API keys, creating a virtual environment with `uv` / `pip` / `conda`, verifying the setup, running Jupyter notebooks and LangGraph Studio, and running the entire course locally with Ollama (no API keys needed).

## Key points

- Python **>=3.12, <3.14** required — **Python 3.13 recommended**; `uv` handles this automatically
- Three install options: `uv` (recommended), `pip`, `conda`
- Two required API keys: **OpenAI** and **Tavily** — both have free alternatives (Ollama, DuckDuckGoSearchRun)
- **DeepSeek** is a 10–35× cheaper alternative to OpenAI; **Ollama** runs everything locally with no API keys
- LangSmith is optional but enables tracing and evaluation
- Primary model: `gpt-5-nano` via `init_chat_model("gpt-5-nano")`. Newer drop-in: `gpt-5.4-nano`
- Verification script `env_utils.py` checks Python version, venv, packages, and env vars

## Notes

### Prerequisites

- Chrome browser (recommended)
- `git`
- One of: `uv` (recommended), `pip`, or `conda`
  - `uv` is also required in Module 2, Lesson 1 to run the MCP server via `uvx`

### Installation

**Step 1 — Clone the repo**

```bash
git clone --depth 1 https://github.com/langchain-ai/lca-lc-foundations.git
cd lca-lc-foundations
```

`--depth 1` downloads only the latest commit — faster than a full clone and sufficient for a course repo you won't contribute to.

**Step 2 — Copy the env file**

```bash
cp example.env .env
```

**Step 3 — Edit `.env` with your API keys**

```dotenv
# Required
OPENAI_API_KEY='your_openai_api_key_here'
TAVILY_API_KEY='your_tavily_api_key_here'

# Optional — only used in Module 1, Lesson 1
ANTHROPIC_API_KEY='your_anthropic_api_key_here'
GOOGLE_API_KEY='your_google_api_key_here'

# Optional — for LangSmith tracing and evaluation
LANGSMITH_API_KEY='your_langsmith_api_key_here'
#LANGSMITH_TRACING=true
LANGSMITH_PROJECT=lca-lc-foundation
# EU instance only:
#LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

**Step 4 — Create virtual environment and install dependencies**

```bash
# Using uv (recommended) — installs Python 3.13 automatically
uv sync

# Using pip
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Using conda — pins to Python 3.13, all packages via pip subsection
conda env create -f environment.yml
conda activate lc-foundations

# Update an existing conda env after requirements change
conda env update -f environment.yml --prune
```

### Dependency versions (May 2026 bump)

Key packages and their current minimum versions:

| Package | Current minimum |
|---|---|
| `langchain` | >=1.3.2 |
| `langchain-core` | >=1.4.0 |
| `langchain-openai` | >=1.2.2 |
| `langchain-anthropic` | >=1.4.4 |
| `langchain-google-genai` | >=4.2.4 |
| `langchain-tavily` | >=0.2.18 |
| `langchain-mcp-adapters` | >=0.2.2 |
| `langgraph` | >=1.2.2 |
| `langgraph-cli` | >=0.4.27 |
| `langsmith` | >=0.8.6 |

### Setup Verification

```bash
# Using uv
uv run python env_utils.py

# Using pip or conda (activate env first)
python env_utils.py
```

The script checks:

- Python executable location and version (>=3.12, <3.14)
- Virtual environment is properly activated
- Required packages installed with correct versions
- Packages are in the correct Python version's site-packages
- Environment variables (API keys) are properly configured

> **Note:** `load_dotenv()` does not override existing system environment variables by default. If you have conflicting keys set globally, the script will detect and warn about them.

### Troubleshooting

**ImportError when running `env_utils.py`**

`ModuleNotFoundError: No module named 'dotenv'` — you're running Python outside the virtual environment.

- With `uv`: use `uv run python env_utils.py`
- With pip/conda: activate the environment first (`source .venv/bin/activate` or `conda activate lc-foundations`)

**Environment Variable Conflicts**

"ENVIRONMENT VARIABLE CONFLICTS DETECTED" — API keys in your system environment differ from `.env`. `load_dotenv()` won't override them.

Solutions:
1. Accept the system value (do nothing)
2. Unset the conflicting system variable for this shell session (commands shown in the warning)
3. Use `load_dotenv(override=True)` in notebooks to force `.env` values
4. Align your `.env` and shell init to use the same values

**LangSmith Tracing Errors**

"LANGSMITH_TRACING is enabled but LANGSMITH_API_KEY still has the placeholder value" — either set a valid key or comment out `LANGSMITH_TRACING=true`. LangSmith is optional.

**Wrong Python Version**

Need Python >=3.12, <3.14. Python 3.14 is not yet supported.

- `uv`: run `uv sync` — auto-installs Python 3.13
- `pip`: install Python 3.13 via pyenv or from python.org
- `conda`: `environment.yml` pins to Python 3.13 automatically

### Running Notebooks

```bash
# Using uv
uv run jupyter lab

# Using pip or conda (activate env first)
jupyter lab
```

Notebooks can also be opened in VSCode, Windsurf, or Cursor.

### Running LangGraph Studio (optional)

```bash
# Must be run from notebooks/module-1 or notebooks/module-3
uv run langgraph dev

# Using pip or conda (activate env first)
langgraph dev
```

### Python Version Management

**uv** — installs Python 3.13 automatically from `pyproject.toml`, runs it with `uv run`. No manual setup needed.

**pyenv + pip** — install Python 3.13, set it locally, create venv:

```bash
pyenv install 3.13
pyenv local 3.13
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**conda** — `environment.yml` pins to `python=3.13`. No manual version management needed.

### Model Providers

#### OpenAI (default)

Primary course model: `gpt-5-nano` — very inexpensive. Newer drop-in: `gpt-5.4-nano` (March 2026).

```python
from langchain.chat_models import init_chat_model
model = init_chat_model(model="gpt-5-nano")
# or use the newer model:
model = init_chat_model(model="gpt-5.4-nano")
```

#### DeepSeek (cheaper alternative — 10–35× lower cost than OpenAI)

```python
# Add to .env: DEEPSEEK_API_KEY='your_key_here'
from langchain_openai import ChatOpenAI
import os

model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1"
)
```

Or use the dedicated integration (from `langchain-deepseek`):

```python
from langchain_deepseek import ChatDeepSeek
model = ChatDeepSeek(model="deepseek-chat")  # reads DEEPSEEK_API_KEY automatically
```

#### Tavily alternative — DuckDuckGoSearchRun (no API key)

If you prefer not to sign up for Tavily:

```python
from langchain_community.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
```

No API key required. Requires `langchain-community` (already in requirements).

#### Ollama — run everything locally (no API keys needed)

All notebooks can be run with local models via Ollama. No API keys, no cost, full privacy.

**1. Install Ollama** from [ollama.com](https://ollama.com).

**2. Pull a model:**

```bash
ollama pull qwen3.5:4b     # recommended for this course
ollama pull llava           # for multimodal notebooks (Module 1, Lesson 4)
```

**Model selection by hardware:**

| Model | VRAM | Best for |
|---|---|---|
| `qwen3.5:4b` (recommended) | ~3.5 GB | All text notebooks — fast and capable |
| `qwen3.5:9b` | ~6 GB | Better reasoning; tight on 6 GB cards |
| `llava` | ~4 GB | Multimodal / image notebooks |

**3. Replace model initialisation in notebooks:**

```python
# Instead of:
from langchain.chat_models import init_chat_model
model = init_chat_model(model="gpt-5-nano")

# Use:
from langchain_ollama import ChatOllama
model = ChatOllama(model="qwen3.5:4b")
```

**4. Structured output** — pass `method="json_mode"` explicitly with Ollama:

```python
structured_model = model.with_structured_output(MySchema, method="json_mode")
```

**5. Keep the model warm** — first load takes 60–100s while the model loads into VRAM. Ollama unloads after 5 minutes of inactivity by default:

```python
model = ChatOllama(model="qwen3.5:4b", keep_alive="1h")   # keep loaded for 1 hour
model = ChatOllama(model="qwen3.5:4b", keep_alive=-1)      # keep until Ollama restarts
```

To change the server-wide default on Windows (persist for your user, then restart Ollama):

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "1h", "User")
```

**6. Reduce VRAM** — default context is 16 384 tokens (~1.6 GB KV cache). Lower it if memory is tight:

```python
model = ChatOllama(model="qwen3.5:4b", num_ctx=4096)
```

**7. Monitor Ollama logs (Windows):**

```powershell
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" -Wait -Tail 20
```

Key lines: `offloaded X/Y layers to GPU` (confirms GPU use) · `eval rate: XX tokens/s` (expect 25–40 t/s for `qwen3.5:4b`).

### Getting Started with LangSmith (optional)

1. Create a [LangSmith account](https://smith.langchain.com/)
2. Create an API key
3. Add to `.env`: `LANGSMITH_API_KEY='your_key'`
4. Uncomment `LANGSMITH_TRACING=true`

Enables tracing of all agent runs, token cost tracking, and evaluation. Not required for the course.

## Quotes worth keeping

> "uv is also required in Module 2, Lesson 1 to run the MCP server with uvx"

## Open questions

- What does `env_utils.py` check exactly for package versions — minimum or exact?

## Related sources

- [[lc-foundations]] — course overview with full module breakdown
- [[lc-foundations-foundational-models]] — Module 1.1, uses the model setup configured here
