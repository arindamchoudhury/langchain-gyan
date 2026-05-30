# Chapter 1: Foundational Models — Initialising, Invoking, and Streaming

> **Source:** [LangChain Academy — Module 1, Lesson 1: Foundational Models](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.1_foundational_models.ipynb` · `1.1_foundational_models_ollama.ipynb`
> **Version:** langchain 1.3.2 · langchain-core 1.4.0 (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- How `init_chat_model` gives you a single, provider-agnostic way to load any LLM
- What an `AIMessage` is and what's inside it
- How to customise model behaviour with parameters like `temperature`
- How to switch between cloud providers (OpenAI, Anthropic, Google, DeepSeek) and local models (Ollama) with minimal code changes
- How `create_agent` wraps a model into a ReAct agent and how to invoke and stream it

---

## The problem this solves

Before LangChain 1.x, every provider had its own class: `ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`. Switching providers meant changing imports and constructor calls throughout your code. `init_chat_model` solves this with a single function that accepts any provider as a string — your application code never needs to change when you swap models.

---

## Core concepts

### The LangChain message model

LangChain represents all LLM interactions as a list of **messages**. There are three kinds:

- `HumanMessage` — what the user says
- `AIMessage` — what the model responds
- `SystemMessage` — instructions that frame the model's behaviour (role, persona, constraints)

When you call `model.invoke("hello")`, LangChain wraps your string in a `HumanMessage` automatically. Every response comes back as an `AIMessage`.

### What `init_chat_model` does

`init_chat_model` is a factory function in `langchain.chat_models`. It:

1. Takes a model name string and optional `model_provider`
2. Loads the correct provider integration package (must be installed separately)
3. Returns a `BaseChatModel` instance with the standard `.invoke()` / `.stream()` / `.batch()` interface

The key insight: **the interface is identical regardless of which provider you use**. `model.invoke(...)` works the same whether the model is GPT, Claude, Gemini, DeepSeek, or a local Ollama model.

### What an `AIMessage` contains

Every model response is an `AIMessage` object with these key attributes:

| Attribute | Type | What it contains |
|---|---|---|
| `.content` | `str` | The actual text response — this is what you display to users |
| `.response_metadata` | `dict` | Provider-specific info: model name, finish reason, token counts |
| `.usage_metadata` | `dict` | Normalised token counts across providers: `input_tokens`, `output_tokens`, `total_tokens` |
| `.tool_calls` | `list` | Tool invocations requested by the model (empty for plain text responses) |
| `.id` | `str` | LangChain's unique run ID for this call (useful for LangSmith tracing) |

### `response_metadata` vs `usage_metadata`

`response_metadata` is **provider-specific** — its structure differs between OpenAI, DeepSeek, and Ollama. Use it for debugging or logging.

`usage_metadata` is **normalised** — LangChain maps every provider's token counts to the same fields. Use this for cost tracking and analytics.

```python
# Provider-specific (structure varies)
response.response_metadata
# {'model_name': 'deepseek-v4-flash', 'finish_reason': 'stop',
#  'token_usage': {'prompt_tokens': 12, 'completion_tokens': 133, 'total_tokens': 145}}

# Normalised (consistent across all providers)
response.usage_metadata
# {'input_tokens': 12, 'output_tokens': 133, 'total_tokens': 145}
```

### `temperature` — controlling randomness

`temperature` controls how deterministic the model's output is:

- `0.0` — fully deterministic, same prompt always gives the same response (best for structured tasks, data extraction, tool use)
- `1.0` — maximum randomness, more creative but less consistent (good for brainstorming, writing)
- `0.7` — a common middle ground for conversational agents

---

## Code examples

### Example 1: Loading a model and making a call

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()  # reads DEEPSEEK_API_KEY / OPENAI_API_KEY / etc. from .env

model = init_chat_model(model="deepseek-chat", model_provider="deepseek")
response = model.invoke("What's the capital of the Moon?")

print(response.content)          # The text answer
print(type(response))             # <class 'langchain_core.messages.ai.AIMessage'>
```

You can also use the `provider:model` shorthand:

```python
model = init_chat_model("deepseek:deepseek-chat")  # equivalent
model = init_chat_model("openai:gpt-5-nano")        # OpenAI
model = init_chat_model("anthropic:claude-sonnet-4-5")  # Anthropic
```

LangChain infers the provider automatically for well-known prefixes:

```python
model = init_chat_model("gpt-5-nano")       # infers: openai
model = init_chat_model("claude-sonnet-4-5") # infers: anthropic
model = init_chat_model("gemini-2.5-flash")  # infers: google_vertexai
```

### Example 2: Inspecting the response

```python
from pprint import pprint

response = model.invoke("What's the capital of the Moon?")

# The answer
print(response.content)

# Provider-specific metadata (good for debugging)
pprint(response.response_metadata)
# {'finish_reason': 'stop',
#  'model_name': 'deepseek-v4-flash',
#  'model_provider': 'deepseek',
#  'token_usage': {'prompt_tokens': 12, 'completion_tokens': 133, 'total_tokens': 145}}

# Normalised token counts (good for cost tracking)
print(response.usage_metadata)
# {'input_tokens': 12, 'output_tokens': 133, 'total_tokens': 145}
```

`finish_reason: 'stop'` means the model completed naturally. Other values you may see: `'length'` (hit max_tokens limit), `'tool_calls'` (model wants to call a tool).

### Example 3: Customising with temperature

```python
# Deterministic — same prompt, same answer
precise_model = init_chat_model("deepseek:deepseek-chat", temperature=0)

# Creative — same prompt, different answers each run
creative_model = init_chat_model("deepseek:deepseek-chat", temperature=1.0)
```

All kwargs after the model name are passed to the underlying provider class. Other useful ones: `max_tokens`, `timeout`, `max_retries`.

### Example 4: Switching providers — DeepSeek dedicated integration

When you need DeepSeek specifically, you can use the dedicated `ChatDeepSeek` class (from `langchain-deepseek`) instead of `init_chat_model`. The interface is identical:

```python
from langchain_deepseek import ChatDeepSeek

# Reads DEEPSEEK_API_KEY from environment automatically
model = ChatDeepSeek(model="deepseek-chat")
response = model.invoke("What's the capital of the Moon?")
print(response.content)
```

**DeepSeek model strings:**

| String | Maps to | Tool calling | Structured output |
|---|---|---|---|
| `deepseek-chat` | DeepSeek-V3 (latest) | Yes | Yes |
| `deepseek-reasoner` | DeepSeek-R1 (thinking) | No | No |

Use `deepseek-chat` for agents. `deepseek-reasoner` is a chain-of-thought reasoning model — it thinks step by step before responding but cannot call tools or return structured JSON.

### Example 5: Local models with Ollama

The Ollama variant uses `ChatOllama` from `langchain-ollama`. Ollama runs models locally — **no API key, no cost, no internet required**.

```python
# langchain-ollama 1.1.0 (May 2026)
# Requires Ollama running locally: https://ollama.com
# Pull a model first: ollama pull qwen3.5:4b
from langchain_ollama import ChatOllama

model = ChatOllama(model="qwen3.5:4b")
response = model.invoke("What's the capital of the Moon?")
print(response.content)
```

**Ollama vs cloud providers — when to use each:**

| | Ollama (local) | Cloud (OpenAI/Anthropic/DeepSeek) |
|---|---|---|
| Cost | Free | Pay per token |
| Privacy | Data stays local | Data sent to provider |
| Speed | Depends on your hardware | Fast, scalable |
| Model quality | Smaller models, lower quality | State-of-the-art |
| Best for | Development, testing, private data | Production, quality-critical tasks |

The `response_metadata` from Ollama looks different (includes `total_duration`, `load_duration`, `eval_count`), but `response.content` is always the same — this is the power of LangChain's unified interface.

### Example 6: Creating and invoking an agent

`create_agent` wraps a model in a **ReAct loop** (Reason + Act). Without tools, it's a stateless single-turn agent. With tools, it loops: think → call tool → observe result → think again — until the model produces a final answer.

```python
from langchain.agents import create_agent
from langchain.messages import HumanMessage

# Create agent — accepts a model string or instance
agent = create_agent("deepseek:deepseek-chat")
# Also works:
# agent = create_agent(model)                     # pass an instance
# agent = create_agent("anthropic:claude-sonnet-4-5")

# Invoke — always pass {"messages": [...]}
response = agent.invoke(
    {"messages": [HumanMessage(content="What's the capital of the Moon?")]}
)
```

**Input:** a dict with a single `"messages"` key containing a list of message objects. Even for a single question, it must be wrapped in a list.

**Output:** the same dict shape — `"messages"` with the model's reply appended to your input:

```python
# What response looks like:
{
    "messages": [
        HumanMessage(content="What's the capital of the Moon?"),  # your input, unchanged
        AIMessage(content="There is no capital...")               # model's reply, appended
    ]
}

# Extracting the answer — always the last message:
print(response["messages"][-1].content)   # just the text
print(response["messages"][-1])           # full AIMessage with token counts, metadata
```

The agent returns the **entire conversation**, not just the last reply. `[-1]` gives the final answer. This design is intentional — the output can feed directly into the next call as conversation history, enabling multi-turn conversations without extra bookkeeping.

### Example 7: Multi-turn conversation with an agent

Pass prior conversation history in the messages list. The agent sees the full context:

```python
from langchain.messages import HumanMessage, AIMessage

response = agent.invoke({
    "messages": [
        HumanMessage(content="What's the capital of the Moon?"),
        AIMessage(content="The capital of the Moon is Luna City."),  # prior assistant turn
        HumanMessage(content="Interesting, tell me more about Luna City"),
    ]
})

print(response["messages"][-1].content)
```

This is how you implement conversation memory manually — by including previous turns in the messages list. In later modules you'll see how LangGraph handles this automatically with a checkpointer.

### Example 8: Streaming tokens

`.invoke()` waits for the full response before returning. `.stream()` returns a generator that yields output token by token as the model produces it — what makes chat UIs feel like text is being typed in real time.

```python
for token, metadata in agent.stream(          # (1) generator, not a blocking call
    {"messages": [HumanMessage(content="Tell me about Luna City")]},  # (2) same input as invoke
    stream_mode="messages"                    # (3) yield individual token chunks
):
    if token.content:                         # (4) skip empty chunks
        print(token.content, end="", flush=True)  # (5) print without newline, unbuffered
```

**What each part does:**

**(1) `agent.stream()`** — returns a generator. Each `next()` call on it gives you the next chunk from the model. The `for` loop drives this automatically.

**(2) Input format** — identical to `.invoke()`. Always a dict with `"messages"`.

**(3) `stream_mode="messages"`** — controls the granularity of what's yielded:

| Mode | Yields |
|---|---|
| `"messages"` | One token chunk per yield — use for real-time display |
| `"values"` | Full graph state snapshot after each node — use for debugging |
| `"updates"` | State delta after each node — use for observability |

**(4) `for token, metadata in ...`** — each yield is a 2-tuple:

- `token` (`AIMessageChunk`) — the partial response so far. `.content` holds the current chunk: could be a word, part of a word, or a space. Same fields as `AIMessage`.
- `metadata` (dict) — graph context: `{"langgraph_node": "agent", "langgraph_step": 1}`. In multi-agent setups tells you which agent produced the chunk.

`if token.content:` filters `""` (empty string) and `None` — chunks with no visible text (tool-call requests, Qwen3 thinking phase). Spaces `" "` are truthy (`bool(" ") == True`) and pass through — they're real content between words.

**(5) `print(token.content, end="", flush=True)`**:

- `end=""` — suppresses the default newline so tokens appear on one continuous line
- `flush=True` — bypasses Python's output buffer and writes to terminal immediately; without it text can appear in bursts rather than one token at a time

**With Ollama / Qwen3:** Qwen3 models enable thinking mode by default. During the reasoning phase, all streaming chunks have `content=""` — so nothing prints until thinking is done. Disable thinking before streaming:

```python
# langchain-ollama 1.1.0 (May 2026)
# Disable thinking mode — otherwise streaming output is silent during reasoning

# Via ChatOllama directly:
model = ChatOllama(model="qwen3.5:4b", think=False)

# Via init_chat_model (provider-agnostic style):
model = init_chat_model("qwen3.5:4b", model_provider="ollama", think=False)

agent = create_agent(model=model)

for token, metadata in agent.stream(
    {"messages": [HumanMessage(content="Tell me about Luna City")]},
    stream_mode="messages"
):
    if token.content:
        print(token.content, end="", flush=True)
```

---

## Common pitfalls

- **Missing provider package** — `init_chat_model("deepseek-chat")` fails with `ImportError` if `langchain-deepseek` isn't installed. Each provider needs its own package: `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-ollama`, `langchain-deepseek`.

- **Wrong DeepSeek model for agents** — `deepseek-reasoner` (DeepSeek-R1) does not support tool calling or structured output. Always use `deepseek-chat` for agents. The error is often cryptic — check the model string first.

- **`response.content` vs `response`** — printing `response` shows the full `AIMessage` object including all metadata. `response.content` is just the text. Use `.content` when you want the answer.

- **`agent.invoke()` output is not a string** — it returns `{"messages": [...]}`, not just the last reply. Access `response["messages"][-1].content` for the final text.

- **Ollama not running** — `ChatOllama` connects to `http://localhost:11434` by default. If Ollama isn't running or the model isn't pulled, you'll get a connection error. Run `ollama pull qwen3.5:4b` before using `ChatOllama(model="qwen3.5:4b")`.

- **`temperature` ignored silently** — some providers (e.g. `deepseek-reasoner`) ignore `temperature`. No error is raised. Check provider docs if your setting has no effect.

- **Qwen3 streaming is silent by default** — Qwen3 models (`qwen3.5:4b`, `qwen3:8b`, etc.) enable thinking mode by default. When streaming, all tokens during the reasoning phase have `content=""` — your `if token.content:` guard suppresses them and nothing appears until thinking completes. Fix: `ChatOllama(model="qwen3.5:4b", think=False)`. Also: never use `think=True` with tool-calling agents — it produces empty output (known Ollama issue).

---

## Exercises

1. **Recall** — What is the difference between `response.response_metadata` and `response.usage_metadata`? When would you use each?

2. **Apply** — Modify Example 1 to use `init_chat_model("anthropic:claude-haiku-4-5")` instead of DeepSeek. What changes in the `response_metadata`? What stays the same?

3. **Extend** — Write a function `cost_estimate(response, input_price_per_1m, output_price_per_1m)` that reads `response.usage_metadata` and returns the estimated cost in USD for that call. Test it with DeepSeek-chat pricing ($0.27/1M input, $1.10/1M output).

---

## Summary

- `init_chat_model(model, model_provider=...)` is the LangChain 1.x standard for loading any LLM — one interface, any provider
- Every response is an `AIMessage` with `.content` (text), `.usage_metadata` (normalised tokens), and `.response_metadata` (provider-specific details)
- `temperature=0` for deterministic tasks, `temperature=1.0` for creativity
- Switching providers only requires changing the model string — the rest of your code stays the same
- `ChatOllama` runs local models with no API key; identical interface to cloud providers
- `create_agent(model)` creates a ReAct agent that takes `{"messages": [...]}` as input and returns the same structure
- The next chapter builds on this by introducing **prompt templates** — structuring what you send to the model instead of plain strings
