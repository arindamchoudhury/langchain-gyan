---
name: lc-foundations-prompting
description: LangChain Module 1.1 prompting — system_prompt, few-shot, structured prompts, structured output with Pydantic
---

# Module 1.1: Prompting

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 1)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.1_prompting.ipynb` · `1.1_prompting_ollama.ipynb`
> **Added:** 2026-05-30
> **Tags:** system_prompt, few-shot, structured-prompt, structured-output, pydantic, response_format, create_agent
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch02-prompting]]

## Summary

Four prompting techniques demonstrated with `create_agent`: basic prompting, system prompt (persona shaping), few-shot examples in the system prompt, structured text prompt (formatting instructions), and structured output via Pydantic `response_format`. Both cloud (DeepSeek) and local (Ollama/Qwen3) variants shown.

## Key points

- `system_prompt` on `create_agent` shapes the agent's persona and output style
- Few-shot examples inside `system_prompt` guide output format via in-context learning
- Structured text prompts constrain output to a fixed schema using plain instructions
- `response_format=PydanticModel` returns a typed Python object in `response["structured_response"]`
- `response['messages'][1]` is the AI reply for single-turn only — prefer `[-1]` for safety

## Notes

### Basic prompting

No system prompt — the agent answers from its default knowledge:

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model=model)

question = HumanMessage(content="What's the capital of the moon?")
response = agent.invoke({"messages": [question]})

print(response['messages'][-1].content)
```

### System prompt

`system_prompt` is a string passed to `create_agent`. It's prepended as a `SystemMessage` before every user message, setting the agent's role, tone, and constraints:

```python
system_prompt = "You are a science fiction writer, create a capital city at the users request."

scifi_agent = create_agent(
    model=model,
    system_prompt=system_prompt
)

response = scifi_agent.invoke({"messages": [question]})
print(response['messages'][-1].content)
```

Without system prompt → factual answer ("The moon has no capital").
With system prompt → creative sci-fi city invented on demand.

### Few-shot examples

Include examples directly in the `system_prompt` to show the model the exact output pattern you want. The model follows the pattern via in-context learning:

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
print(response['messages'][-1].content)
# Output: "Lunaris Prime"  (DeepSeek) / "Lunovia"  (Ollama)
```

Few-shot effect: the model learns the short, one-word city-name style from the examples and mirrors it.

### Structured prompt (text-based)

Add formatting instructions to `system_prompt` to constrain the structure of the text output:

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
print(response['messages'][-1].content)
# Output follows Name/Location/Vibe/Economy structure as plain text
```

This is prompt engineering — the output is still a string, just formatted predictably. For truly typed output, use `response_format` (next section).

### Structured output with Pydantic

`response_format` accepts a Pydantic `BaseModel` subclass. The agent forces the model to return data matching the schema and validates it automatically. The result is in `response["structured_response"]`:

```python
from pydantic import BaseModel

class CapitalInfo(BaseModel):
    name: str
    location: str
    vibe: str
    economy: str

agent = create_agent(
    model=model,
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
    response_format=CapitalInfo
)

question = HumanMessage(content="What is the capital of The Moon?")
response = agent.invoke({"messages": [question]})

# Typed Pydantic instance
capital = response["structured_response"]
print(capital)
# CapitalInfo(name='Lunar Prime', location='The Mare Imbrium basin...', ...)

# Access fields directly
print(capital.name)       # 'Lunar Prime'
print(capital.location)   # 'The Mare Imbrium basin, near the lunar equator'

# f-string example
print(f"{capital.name} is a city located at {capital.location}")
```

**Output structure with `response_format`:**

```python
{
    "messages": [...],                           # full conversation as before
    "structured_response": CapitalInfo(...)      # validated Pydantic instance ← new
}
```

Without `response_format`, `response` only has `"messages"`. With it, `"structured_response"` is added.

### `messages[1]` vs `messages[-1]`

The notebook uses `response['messages'][1]`. This works for single-turn only:

```
messages[0] = HumanMessage  (your input)
messages[1] = AIMessage     (first AI reply)
```

In multi-turn conversations or when the agent uses tools, there are more messages — `[1]` would not be the final answer. Always use `[-1]`:

```python
print(response['messages'][-1].content)  # ← always the final AI reply
```

### Ollama variant

Identical code — swap `ChatDeepSeek` for `ChatOllama`. No `load_dotenv()` needed. Structured output (`response_format`) works the same with Ollama/Qwen3:

```python
from langchain_ollama import ChatOllama

model = ChatOllama(model="qwen3.5:4b")
agent = create_agent(
    model=model,
    system_prompt="You are a science fiction writer, create a capital city at the users request.",
    response_format=CapitalInfo
)
```

## Open questions

- How does `response_format` behave when the model fails to produce valid JSON — does it retry automatically?
- Can `system_prompt` and `response_format` be changed between invocations on the same agent?

## Related sources

- [[lc-foundations-foundational-models]] — `create_agent` basics, invoke, streaming
- [[ch02-prompting]] — full pedagogical chapter with best practices and pitfalls
