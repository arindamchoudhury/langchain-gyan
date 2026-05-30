---
name: lc-foundations-foundational-models
description: LangChain Module 1.1 — init_chat_model, AIMessage, create_agent, streaming, Ollama local models
---

# Module 1.1: Foundational Models

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 1)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.1_foundational_models.ipynb` · `1.1_foundational_models_ollama.ipynb`
> **Added:** 2026-05-30
> **Tags:** init_chat_model, AIMessage, create_agent, streaming, ollama, deepseek, temperature, model-providers
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch01-foundational-models]] — includes deeper explanations, best practices, exercises.

## Summary

Two notebooks introducing the core LangChain pattern: load a model → invoke it → read the response. The main notebook uses cloud providers (DeepSeek, Google). The Ollama variant shows the same pattern with local models. Both end with `create_agent` — a pre-built ReAct agent that the rest of the course builds on.

## Key points

- `init_chat_model(model, model_provider=...)` is the LangChain 1.x unified model loader — one interface for every provider
- Provider can be inferred from model name: `gpt-*` → openai, `claude*` → anthropic, `gemini*` → google_vertexai
- Every model response is an `AIMessage` — access `.content` for text, `.usage_metadata` for normalised token counts
- `temperature=0` → deterministic; `temperature=1.0` → creative/random
- `ChatOllama` runs local models — no API key, no cost, identical interface to cloud providers
- `create_agent(model)` creates a ReAct agent; takes `{"messages": [...]}` input, returns same structure
- `agent.stream(..., stream_mode="messages")` yields `(AIMessageChunk, metadata)` tuples per token
- Qwen3 models enable **thinking mode by default** — streaming chunks during reasoning have `content=""`, nothing prints; disable with `think=False` (Ollama API param) or `reasoning=False` (LangChain param)

## Notes

### `init_chat_model`

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# With explicit provider
model = init_chat_model(model="deepseek-chat", model_provider="deepseek")

# Shorthand: provider:model
model = init_chat_model("openai:gpt-5-nano")

# Provider inferred from name
model = init_chat_model("gpt-5-nano")        # → openai
model = init_chat_model("claude-sonnet-4-5") # → anthropic
```

Requires the provider package installed: `langchain-deepseek`, `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`.

### Invoking a model

```python
response = model.invoke("What's the capital of the Moon?")

# The text answer
print(response.content)

# Normalised token counts (consistent across providers)
print(response.usage_metadata)
# {'input_tokens': 12, 'output_tokens': 133, 'total_tokens': 145}

# Provider-specific metadata (varies by provider)
from pprint import pprint
pprint(response.response_metadata)
# {'model_name': 'deepseek-v4-flash', 'finish_reason': 'stop', 'token_usage': {...}}
```

### Customising the model

```python
model = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
    temperature=1.0   # 0.0 = deterministic, 1.0 = creative
)
```

### DeepSeek dedicated integration

```python
from langchain_deepseek import ChatDeepSeek

model = ChatDeepSeek(model="deepseek-chat")  # reads DEEPSEEK_API_KEY from env
```

**Model strings:**

| String | Model | Tool calling |
|---|---|---|
| `deepseek-chat` | DeepSeek-V3 | Yes — use for agents |
| `deepseek-reasoner` | DeepSeek-R1 | No — thinking model only |

### Google Gemini

```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
response = model.invoke("What's the capital of the Moon?")
print(response.content)
```

### Local models — Ollama

Two equivalent ways to load an Ollama model:

```python
# Option A: ChatOllama directly
from langchain_ollama import ChatOllama
model = ChatOllama(model="qwen3.5:4b")

# Option B: init_chat_model — keeps code provider-agnostic
from langchain.chat_models import init_chat_model
model = init_chat_model("qwen3.5:4b", model_provider="ollama")
# or shorthand:
model = init_chat_model("ollama:qwen3.5:4b")
```

> **Note:** Ollama model names (`qwen3.5:4b`, `llama3.2`, etc.) are **not auto-inferred** by `init_chat_model` — unlike `gpt-*` (→ openai) or `claude*` (→ anthropic). Always specify `model_provider="ollama"` explicitly.

```python
# Requires: Ollama running locally + model pulled (ollama pull qwen3.5:4b)
response = model.invoke("What's the capital of the Moon?")
print(response.content)  # same interface as cloud providers
```

Ollama `response_metadata` includes local perf stats (`total_duration`, `load_duration`, `eval_count`) instead of API-style token usage — but `usage_metadata` is always normalised.

**Qwen3 thinking mode** — Qwen3 models enable thinking by default. For plain `invoke()` this is fine (thinking tokens are hidden in `response_metadata`). For streaming, thinking-phase chunks have `content=""` and nothing prints until reasoning is done. Disable it:

```python
# Ollama API param (used in the notebook)
model = ChatOllama(model="qwen3.5:4b", think=False)

# LangChain documented param (equivalent)
model = ChatOllama(model="qwen3.5:4b", reasoning=False)
```

> ⚠️ `think=True` + tool calling = empty output (Ollama issue). Always use `think=False` when building agents with tools.

### `create_agent` — pre-built ReAct agent

```python
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage

agent = create_agent("deepseek:deepseek-chat")  # string or model instance
```

**`agent.invoke()` — input and output**

Input is always a dict with a `"messages"` key containing a list of messages:

```python
# Single-turn
response = agent.invoke(
    {"messages": [HumanMessage(content="What's the capital of the Moon?")]}
)
```

Output is the same dict shape — `"messages"` with the **full conversation** appended:

```python
# Output structure:
{
    "messages": [
        HumanMessage(content="What's the capital of the Moon?"),  # your input
        AIMessage(content="There is no capital...")               # model's reply
    ]
}

# Get just the final answer:
print(response["messages"][-1].content)   # last message = model's reply
print(response["messages"][-1])           # full AIMessage with metadata
```

The agent appends its reply to the input list and returns the whole thing. `[-1]` is always the model's final answer. This design makes it easy to chain turns — the output becomes the input for the next call:

```python
# Multi-turn — pass history manually
response = agent.invoke({
    "messages": [
        HumanMessage(content="What's the capital?"),
        AIMessage(content="Luna City."),     # previous assistant turn
        HumanMessage(content="Tell me more"),
    ]
})
# response["messages"][-1] = new AIMessage continuing the conversation
```

### Streaming tokens

With cloud providers (DeepSeek, OpenAI, Anthropic), streaming works as-is.

**Line-by-line breakdown:**

```python
for token, metadata in agent.stream(          # (1)
    {"messages": [HumanMessage(content="...")]},  # (2)
    stream_mode="messages"                    # (3)
):
    if token.content:                         # (4)
        print(token.content, end="", flush=True)  # (5)
```

**(1) `agent.stream(...)`** — instead of waiting for the full response (`.invoke()`), `.stream()` returns a generator that yields output piece by piece as the model produces it. This is what makes UIs feel like text is being typed in real time.

**(2) `{"messages": [HumanMessage(...)]}`** — the input format. LangGraph agents always take a dict with a `"messages"` key. `HumanMessage` wraps the user's text so the agent knows it's a user turn.

**(3) `stream_mode="messages"`** — controls what gets yielded each iteration:

| Mode | Yields |
|---|---|
| `"messages"` | Individual token chunks as they stream |
| `"values"` | Full graph state after each node completes |
| `"updates"` | Only what changed in state after each node |

Use `"messages"` for real-time token display.

**(4) `if token.content:`** — each yield is a tuple `(token, metadata)`:

- `token` — an `AIMessageChunk`: same structure as `AIMessage` but partial; `.content` holds the current chunk (a word, syllable, or space)
- `metadata` — dict with graph info e.g. `{"langgraph_node": "agent"}` — useful in multi-agent graphs to know which agent is speaking

The guard filters `""` (empty string) and `None`. Spaces `" "` are truthy (`bool(" ") == True`) and pass through — without them words would run together.

**(5) `print(token.content, end="", flush=True)`**:

- `end=""` — suppresses the newline `print` normally adds, so tokens appear on the same line
- `flush=True` — forces output to terminal immediately rather than buffering; without it text appears in bursts

With Qwen3 via Ollama, disable thinking mode first — otherwise streaming chunks during the reasoning phase have `content=""` and nothing prints:

```python
# langchain-ollama 1.1.0 (May 2026)
# Qwen3 enables thinking mode by default — disable for streaming
model = ChatOllama(model="qwen3.5:4b", think=False)
agent = create_agent(model=model)

for token, metadata in agent.stream(
    {"messages": [HumanMessage(content="Tell me about Luna City")]},
    stream_mode="messages"
):
    if token.content:  # filters "" and None only — spaces " " are truthy and pass through
        print(token.content, end="", flush=True)
```

**Why spaces pass through `if token.content:`:**
`bool(" ") == True` in Python — a space is non-empty and truthy. Only `""` and `None` are filtered out. Spaces must pass through or words run together (`TheMoonhasnocapital`). What actually gets blocked: tool-call-only chunks (`content=""`) and Qwen3 thinking-phase chunks (`content=""`).

`metadata` contains `langgraph_node` — which graph node produced the token. Useful for multi-agent routing later.

## Open questions

- How does `create_agent` behave differently when `tools=[]` is passed vs no tools at all?
- What other `stream_mode` values exist besides `"messages"`?

## Related sources

- [[lc-foundations-getting-set-up]] — environment setup required before running these notebooks
- [[ch01-foundational-models]] — full pedagogical chapter with pitfalls and exercises
