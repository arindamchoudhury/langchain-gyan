# Chapter 2: Prompting — System Prompts, Few-Shot, and Structured Output

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 1)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.1_prompting.ipynb` · `1.1_prompting_ollama.ipynb`
> **Version:** langchain 1.3.2 · langchain-core 1.4.0 (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- How `system_prompt` shapes an agent's persona and output style
- What few-shot prompting is and how to write effective examples
- The difference between a structured text prompt and typed structured output
- How to get a validated Pydantic object back from an agent with `response_format`
- Why `messages[-1]` is safer than `messages[1]`

---

## The problem this solves

A bare `create_agent(model=model)` answers from the model's default training — helpful, but generic. Real applications need control: a customer support agent should stay on-topic; a data extraction agent should return consistent fields; a creative writing tool should match a particular style. Prompting is the mechanism that shapes all of this before a single line of business logic is written.

---

## Core concept

Every message the agent sees is one of three types:

| Type | Purpose |
|---|---|
| `SystemMessage` | Instructions framing how the model should behave — always first |
| `HumanMessage` | What the user says |
| `AIMessage` | What the model replies |

The `system_prompt` string you pass to `create_agent` becomes a `SystemMessage` that is **prepended to every invocation**. The model reads it before the user's message and uses it to decide how to respond.

Think of it as the job description you give an employee. Without one, they'll do a reasonable job based on general knowledge. With one, they know their role, constraints, and preferred output format.

**Four techniques shown in this lesson — ordered from least to most structured:**

1. **No system prompt** — model uses default knowledge
2. **System prompt** — defines persona and purpose
3. **Few-shot examples** — show the model examples of the exact output style you want
4. **Structured prompt** — formatting instructions in the prompt (still returns a string)
5. **Structured output** — `response_format` with a Pydantic model (returns a typed Python object)

---

## Code examples

### Example 1: Basic vs system prompt — the difference

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
question = HumanMessage(content="What's the capital of the moon?")

# No system prompt — factual, generic answer
agent = create_agent(model=model)
response = agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# "The Moon has no capital — it's a natural satellite with no government."

# With system prompt — takes on a new persona
scifi_agent = create_agent(
    model=model,
    system_prompt="You are a science fiction writer, create a capital city at the users request."
)
response = scifi_agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# "The capital of the Moon is Ariana — a domed metropolis in the Sea of Tranquility..."
```

The only change is `system_prompt`. Everything else is identical. This is the leverage of prompting.

### Example 2: Few-shot examples in the system prompt

Few-shot prompting embeds input→output examples directly in the system prompt. The model learns the pattern and applies it to the user's actual question:

```python
system_prompt = """
You are a science fiction writer, create a space capital city at the users request.

User: What is the capital of mars?
Scifi Writer: Marsialis

User: What is the capital of Venus?
Scifi Writer: Venusovia

"""

scifi_agent = create_agent(model=model, system_prompt=system_prompt)
response = scifi_agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# "Lunaris Prime"  — one short name, matching the example pattern
```

Without the examples the model wrote paragraphs. With two examples showing one-word city names, it learned the expected style and followed it. The examples are the training signal.

### Example 3: Structured prompt (text output)

Add formatting instructions to constrain the shape of the text output:

```python
system_prompt = """
You are a science fiction writer, create a space capital city at the users request.

Please keep to the below structure.

Name: The name of the capital city

Location: Where it is based

Vibe: 2-3 words to describe its vibe

Economy: Main industries

"""

scifi_agent = create_agent(model=model, system_prompt=system_prompt)
response = scifi_agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# Name: Mare Imbrium Station
# Location: Burrowed into the edge of the Mare Imbrium...
# Vibe: Silent opulence, monastic surveillance
# Economy: Crystal manufacturing, private data storage...
```

This works well and requires no extra dependencies. The tradeoff: the output is still a string. Parsing it into fields requires regex or string splitting. For reliable field extraction, use `response_format` instead.

### Example 4: Structured output with Pydantic

Define a Pydantic `BaseModel`, pass it as `response_format`, and get a validated Python object back:

```python
from pydantic import BaseModel, Field

class CapitalInfo(BaseModel):
    name: str = Field(description="The name of the capital city")
    location: str = Field(description="Where on the planet or moon it is located")
    vibe: str = Field(description="2-3 words describing the city's atmosphere and character")
    economy: str = Field(description="The main industries that drive the city's economy")

agent = create_agent(
    model=model,
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
    response_format=CapitalInfo
)

response = agent.invoke({"messages": [HumanMessage(content="What is the capital of The Moon?")]})

# Typed Pydantic instance — not a string
capital = response["structured_response"]
print(capital)
# CapitalInfo(name='Lunar Prime', location='The Mare Imbrium basin, near the lunar equator',
#             vibe='Silent, ethereal, resilient...', economy='Helium-3 mining, zero-g manufacturing...')

# Access fields with dot notation — type-safe
print(capital.name)
print(f"{capital.name} is located at {capital.location}")
```

**What changed in the output dict:**

```python
# Without response_format:
{"messages": [HumanMessage, AIMessage]}

# With response_format:
{"messages": [HumanMessage, AIMessage],
 "structured_response": CapitalInfo(...)}   # ← typed Pydantic instance added
```

LangChain selects the best extraction strategy automatically based on model capability (native JSON mode, tool calling, or prompt-based). The result is always validated against the Pydantic schema before being returned.

### Example 5: Ollama — same code, swap the model

```python
# langchain-ollama 1.1.0 (May 2026)
from langchain_ollama import ChatOllama

model = ChatOllama(model="qwen3.5:4b")

agent = create_agent(
    model=model,
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
    response_format=CapitalInfo
)

response = agent.invoke({"messages": [HumanMessage(content="What is the capital of The Moon?")]})
capital = response["structured_response"]
print(capital.name)  # 'The Luminous Spires'
```

No `load_dotenv()` needed — Ollama runs locally. Structured output works identically.

---

## Best practices

- **Add field descriptions to Pydantic models** — `Field(description="...")` helps the model understand what each field means, improving extraction accuracy especially with complex schemas
- **Keep system prompts focused** — one clear role per agent. A system prompt that says "you are a writer AND a data analyst AND a customer service rep" confuses the model
- **Few-shot examples should match the exact format you want** — if you want one-word answers, your examples should be one word. The model learns style from the examples, not just content
- **Use `response_format` instead of regex parsing** — structured prompts + string parsing breaks when the model adds an extra line or changes spacing; Pydantic handles this robustly
- **System prompt is not a security boundary** — a determined user can prompt-inject past it. Don't rely on `system_prompt` alone to enforce security constraints

---

## Common pitfalls

- **`messages[1]` only works for single-turn** — the notebook uses `response['messages'][1]` which is the AI reply when there's exactly one human message and no tools. In multi-turn conversations or tool-using agents there are more messages at index 1. Always use `response["messages"][-1]` for the final answer.

- **`structured_response` key missing** — if you forget `response_format`, the key doesn't exist. Accessing `response["structured_response"]` raises `KeyError`. Always set `response_format` if you need the typed output.

- **Pydantic field type mismatches** — if the model returns `"lots of things"` for a field typed as `list[str]`, validation fails. LangChain will retry, but use `str` for free-form fields and `list` only when you're confident the model will return a list.

- **Ollama structured output requires compatible model** — some Ollama models don't support JSON/structured output reliably. `qwen3.5:4b` works well. If you get empty or malformed `structured_response`, try a larger model or add explicit JSON instructions to the system prompt.

- **Few-shot examples in system prompt count toward token usage** — long example lists add input tokens on every call. Keep examples concise, especially if the agent will handle high call volume.

---

## Exercises

1. **Recall** — What is the difference between a structured prompt and structured output with `response_format`? When would you choose one over the other?

2. **Apply** — Add a `population: int` field to `CapitalInfo` and re-run the structured output example. Does the model return a valid integer? What happens if it returns something like `"about 2 million"`?

3. **Extend** — Build an agent that extracts structured data from unstructured text. Pass a paragraph of news text as the user message, define a Pydantic model with fields like `headline`, `date`, `location`, `key_people: list[str]`, and have the agent populate it.

---

## Summary

- `system_prompt` on `create_agent` prepends a `SystemMessage` before every user message — the model reads it first and adjusts its behavior accordingly
- Few-shot examples in `system_prompt` teach output style via in-context learning — the model mirrors the examples
- Structured text prompts constrain output shape but still return a string
- `response_format=PydanticModel` returns a validated typed object in `response["structured_response"]` — no parsing needed
- Use `messages[-1]` not `messages[1]` — safe for all agent configurations
- The next chapter builds on this with **tools** — giving the agent the ability to take actions beyond generating text
