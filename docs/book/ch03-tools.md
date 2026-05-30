# Chapter 3: Tools — Giving Agents the Ability to Act

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 2)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.2_tools.ipynb`
> **Version:** langchain 1.3.2 (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- How to turn any Python function into a tool with the `@tool` decorator
- What the tool's name and description do — and why they matter
- How to attach tools to an agent with `create_agent(tools=[...])`
- The exact four-message flow that happens when an agent calls a tool
- How to inspect which tool was called and with what arguments

---

## The problem this solves

A language model can only generate text. It cannot calculate square roots accurately, look up live data, run queries, or send emails — it can only *describe* doing those things. Tools bridge that gap: they are Python functions the agent is allowed to call. The model decides *when* to call them and *what arguments to pass*; your code actually runs them. Without tools, an agent is a very sophisticated autocomplete. With tools, it can take real actions.

---

## Core concept

LangChain uses the **ReAct loop** (Reasoning + Acting) under the hood:

```
User message
    → Model reasons: "I need to calculate sqrt(467). I have square_root tool."
    → Model emits a tool_call (not text — a structured request)
    → LangChain intercepts, runs your Python function
    → Result returned to model as a ToolMessage
    → Model composes the final answer
```

This loop can repeat — the model can call multiple tools in sequence before answering. The full conversation is preserved in `response["messages"]` so you can see every step.

The `@tool` decorator does two things: it wraps your function as a `BaseTool` object, and it extracts the **schema** (from type annotations) and **description** (from the docstring) that the model reads to understand the tool. If the description is vague, the model may call the wrong tool or skip it entirely.

---

## Code examples

### Example 1: The three forms of `@tool`

```python
# langchain 1.3.2 (May 2026)
from langchain.tools import tool

# Form 1: bare @tool — name inferred from function name, description from docstring
@tool
def square_root(x: float) -> float:
    """Calculate the square root of a number"""
    return x ** 0.5

# Form 2: explicit name — useful when function name is internal/ambiguous
@tool("square_root")
def tool1(x: float) -> float:
    """Calculate the square root of a number"""
    return x ** 0.5

# Form 3: explicit name + explicit description — no docstring required
@tool("square_root", description="Calculate the square root of a number")
def tool1(x: float) -> float:
    return x ** 0.5
```

All three produce an identical tool from the model's perspective. Use Form 1 for most cases. Use Form 3 when you want to keep the description in code rather than a docstring.

**Description precedence:** `description=` argument → docstring → `args_schema` description.

### Example 2: Test a tool directly before wiring it to an agent

```python
# Tools are callable via .invoke() — no agent needed
result = tool1.invoke({"x": 467})
print(result)  # 21.61018278497431
```

Always test tools in isolation first. If `.invoke()` fails, the agent will fail too — and the error will be much harder to diagnose inside an agent run.

### Example 3: Attach tools to an agent

```python
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")

agent = create_agent(
    model=model,
    tools=[tool1],
    system_prompt="You are an arithmetic wizard. Use your tools to calculate the square root and square of any number."
)

question = HumanMessage(content="What is the square root of 467?")
response = agent.invoke({"messages": [question]})

print(response["messages"][-1].content)
# "The square root of **467** is approximately **21.6102**."
```

`tools=` takes a list — you can pass multiple tools. The model chooses which one to call based on names and descriptions.

### Example 4: Inspect the full message flow

```python
from pprint import pprint

pprint(response["messages"])
```

```
[
  HumanMessage(content='What is the square root of 467?'),

  AIMessage(content='',
            tool_calls=[{'name': 'square_root',
                         'args': {'x': 467},
                         'id': 'call_00_E5kDq6...',
                         'type': 'tool_call'}]),

  ToolMessage(content='21.61018278497431',
              name='square_root',
              tool_call_id='call_00_E5kDq6...'),

  AIMessage(content='The square root of **467** is approximately **21.6102**.')
]
```

Four messages every time the agent uses a tool:

| # | Type | Content |
|---|---|---|
| 0 | `HumanMessage` | User's original question |
| 1 | `AIMessage` | Empty text; `tool_calls` list tells LangChain what to run |
| 2 | `ToolMessage` | Your function's return value, as a string |
| 3 | `AIMessage` | Final natural-language answer |

```python
# Inspect what the model decided to call
print(response["messages"][1].tool_calls)
# [{'name': 'square_root', 'args': {'x': 467}, 'id': '...', 'type': 'tool_call'}]
```

The `id` field links `AIMessage.tool_calls[n]` to the matching `ToolMessage.tool_call_id`. LangChain handles this automatically.

---

## Best practices

- **Type-annotate every parameter** — `@tool` infers the JSON schema from annotations. An unannotated parameter gets `Any`, which gives the model no guidance on what to pass
- **Write a precise, action-oriented docstring** — "Calculate the square root of a number" is good. "Does math stuff" is not. The model reads this to decide when to call the tool
- **Use snake_case names** — model providers normalise tool names; snake_case is safest across all providers
- **Test with `.invoke()` before attaching to an agent** — a tool that raises an exception will cause the agent to fail with a confusing error
- **Keep tools focused** — one tool per action. A tool that "does everything" gives the model no useful signal about when to use it

---

## Common pitfalls

- **Missing type annotations** — if a parameter has no type hint, the model may pass the wrong type (e.g. `"467"` instead of `467.0`). Always annotate.

- **Vague description leads to wrong tool choice** — if you have two tools with similar descriptions, the model may call the wrong one. Make descriptions distinct and specific about what the tool does and when to use it.

- **Forgetting `load_dotenv()`** — `ChatDeepSeek` reads `DEEPSEEK_API_KEY` from the environment. Without `load_dotenv()`, the model constructor raises an auth error before any tool logic runs.

- **Using `messages[1]` for the final answer** — with tool use, `messages[1]` is the `AIMessage` with the tool call (empty `.content`). The final answer is always `messages[-1]`. This is a harder bug to catch because it silently returns an empty string.

- **Tool return values are always strings** — LangChain converts your function's return value to a string for the `ToolMessage`. If you return a `dict` or a `float`, it becomes its string representation. The model then parses it from text. For complex return types, return a JSON string explicitly.

---

## Exercises

1. **Recall** — What are the four message types that appear in `response["messages"]` when an agent calls a tool? What does each one contain?

2. **Apply** — Add a second tool `square(x: float) -> float` that returns `x ** 2`. Pass both tools to `create_agent` and ask the agent: "What is the square root of 144 plus the square of 3?" Inspect `response["messages"]` to see how many tool calls were made.

3. **Extend** — Build a `word_count(text: str) -> int` tool that counts words. Create an agent that uses it to analyse user-provided text. What happens if you ask the agent a question that doesn't need the tool — does it still call it?

---

## Summary

- `@tool` wraps a Python function as a `BaseTool` — the decorator has three forms differing in how name and description are supplied
- Type annotations define the tool's argument schema; the docstring (or `description=`) tells the model when to use it
- `create_agent(tools=[...])` passes tools to the ReAct agent; the model selects which to call based on name and description
- Every tool call produces 4 messages: `HumanMessage` → `AIMessage(tool_calls)` → `ToolMessage` → `AIMessage(final)`
- `response["messages"][1].tool_calls` shows the tool name, args, and id for each call
- The next chapter builds on this with **short-term memory** — giving the agent the ability to remember earlier turns in a conversation
