---
name: lc-foundations-tools
description: LangChain Module 1.2 tools — @tool decorator (three forms), adding tools to create_agent, tool-call message flow (HumanMessage → AIMessage with tool_calls → ToolMessage → AIMessage)
---

# Module 1.2: Tools

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 2)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.2_tools.ipynb`
> **Added:** 2026-05-30
> **Tags:** tool, @tool, create_agent, tools, ToolMessage, tool_calls, ReAct
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch03-tools]]

## Summary

How to define Python functions as LangChain tools using the `@tool` decorator, attach them to an agent with `create_agent(tools=[...])`, and understand the four-message exchange that happens when the agent uses a tool.

## Key points

- `@tool` has three forms: bare decorator, name-only, name+description
- The function's type annotations become the tool's input schema — required
- The docstring (or `description=` arg) is what the model reads to decide when to call the tool
- `create_agent(tools=[...])` accepts a list — agents can have multiple tools
- Tool use produces 4 messages: Human → AI(tool_calls) → Tool → AI(final answer)
- `response["messages"][1].tool_calls` exposes which tool was called and with what args

## Notes

### Defining a tool — three forms

```python
# langchain 1.3.2 (May 2026)
from langchain.tools import tool

# Form 1: bare @tool — name from function, description from docstring
@tool
def square_root(x: float) -> float:
    """Calculate the square root of a number"""
    return x ** 0.5

# Form 2: explicit name — description still from docstring
@tool("square_root")
def tool1(x: float) -> float:
    """Calculate the square root of a number"""
    return x ** 0.5

# Form 3: explicit name + description — no docstring needed
@tool("square_root", description="Calculate the square root of a number")
def tool1(x: float) -> float:
    return x ** 0.5
```

The model sees the tool's name and description when deciding whether to call it. The type annotations define the JSON schema for the tool's arguments.

### Invoking a tool directly

Tools can be called without an agent using `.invoke()`:

```python
tool1.invoke({"x": 467})
# 21.61018278497431
```

### Adding tools to an agent

Pass a list to `create_agent(tools=[...])`:

```python
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent

model = ChatDeepSeek(model="deepseek-chat")

agent = create_agent(
    model=model,
    tools=[tool1],
    system_prompt="You are an arithmetic wizard. Use your tools to calculate the square root and square of any number."
)
```

### The tool-call message flow

When the agent uses a tool, four messages appear in `response["messages"]`:

```python
from langchain.messages import HumanMessage
from pprint import pprint

question = HumanMessage(content="What is the square root of 467?")
response = agent.invoke({"messages": [question]})

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

| Index | Type | What it contains |
|---|---|---|
| `[0]` | `HumanMessage` | User's question |
| `[1]` | `AIMessage` | Empty content; `tool_calls` list with name, args, id |
| `[2]` | `ToolMessage` | Tool result as string; matched back via `tool_call_id` |
| `[-1]` | `AIMessage` | Final answer incorporating the tool result |

### Inspecting tool calls

```python
print(response["messages"][1].tool_calls)
# [{'name': 'square_root', 'args': {'x': 467}, 'id': '...', 'type': 'tool_call'}]
```

Each entry has `name`, `args` (dict), `id` (for matching to ToolMessage), and `type`.

## Open questions

- What happens when the model calls a tool that doesn't exist or passes wrong argument types?
- Can `return_direct=True` be used to short-circuit the final LLM call?

## Related sources

- [[lc-foundations-foundational-models]] — `create_agent` basics, invoke, streaming
- [[lc-foundations-prompting]] — system_prompt, structured output
- [[ch03-tools]] — full pedagogical chapter
