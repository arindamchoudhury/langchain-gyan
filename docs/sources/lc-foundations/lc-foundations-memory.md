---
name: lc-foundations-memory
description: LangChain Module 1.3 memory — InMemorySaver checkpointer, thread_id, stateless vs stateful agent behaviour, full message history in response
---

# Module 1.3: Short-Term Memory

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 3)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.3_memory.ipynb`
> **Added:** 2026-05-30
> **Tags:** memory, InMemorySaver, checkpointer, thread_id, stateful, short-term-memory
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch05-memory]]

## Summary

Demonstrates the stateless default behaviour of `create_agent` — each call starts fresh — then fixes it with `InMemorySaver` and `thread_id`. Shows that memory works by replaying full message history on every invoke, which is visible in the growing `response["messages"]` and rising input token counts.

## Key points

- By default `create_agent` is stateless — each `.invoke()` receives only the messages you pass
- `InMemorySaver` stores the full conversation history keyed by `thread_id`
- `config = {"configurable": {"thread_id": "1"}}` is passed on every `.invoke()` call
- With memory, `response["messages"]` contains the complete history — not just the current exchange
- Token usage grows with conversation length — memory is not free
- `InMemorySaver` is for development only; use `PostgresSaver` in production

## Notes

### No memory — stateless by default

Each `agent.invoke()` call is independent. The second call has no knowledge of the first:

```python
# langchain 1.3.2 · langgraph 1.2.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model)

# Turn 1
response = agent.invoke({"messages": [HumanMessage(content="Hello my name is Seán and my favourite colour is green")]})
# AIMessage: "Hello Seán! Green is a wonderful colour..."
# input_tokens: 16

# Turn 2 — agent has no memory of turn 1
response = agent.invoke({"messages": [HumanMessage(content="What's my favourite colour?")]})
# AIMessage: "I don't know your favourite colour, since we've never met..."
# input_tokens: 10  ← only the new question was sent
```

The second call's `response["messages"]` has only 2 entries — the new HumanMessage and the AIMessage. Nothing from turn 1.

### Adding memory with InMemorySaver

Pass `InMemorySaver()` as the `checkpointer` parameter, and a `config` with `thread_id` on every `.invoke()`:

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model,
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "1"}}

# Turn 1
response = agent.invoke(
    {"messages": [HumanMessage(content="Hello my name is Seán and my favourite colour is green")]},
    config,
)
# input_tokens: 16

# Turn 2 — agent remembers turn 1
response = agent.invoke(
    {"messages": [HumanMessage(content="What's my favourite colour?")]},
    config,
)
# AIMessage: "Based on what you told me earlier, your favourite colour is green. 😊"
# input_tokens: 79  ← full history passed
```

### What response["messages"] contains with memory

After turn 2, `response["messages"]` has 4 entries — the full conversation:

```
[0] HumanMessage("Hello my name is Seán and my favourite colour is green")
[1] AIMessage("Hello Seán! Green is a wonderful colour...")
[2] HumanMessage("What's my favourite colour?")
[3] AIMessage("Based on what you told me earlier, your favourite colour is green.")
```

The checkpointer appends new messages to the stored history and returns everything.

### thread_id — separating conversations

`thread_id` is the key that identifies a conversation thread. Use different IDs for different users or sessions:

```python
config_user_a = {"configurable": {"thread_id": "user-a"}}
config_user_b = {"configurable": {"thread_id": "user-b"}}

agent.invoke({"messages": [HumanMessage("My name is Alice")]}, config_user_a)
agent.invoke({"messages": [HumanMessage("My name is Bob")]}, config_user_b)

# Each thread is isolated — user-a has no knowledge of user-b's messages
```

### Token cost of memory

Token counts read directly from `response["messages"][-1].usage_metadata["input_tokens"]` in the notebook output — reported by the DeepSeek API, not estimated:

```python
response["messages"][-1].usage_metadata["input_tokens"]
```

| | Input tokens |
|---|---|
| Turn 1 (no memory) | 16 |
| Turn 2 (no memory) | 10 |
| Turn 1 (with memory) | 16 |
| Turn 2 (with memory) | 79 |

Turn 2 jumps from 10 → 79 because the full prior exchange is replayed into the model's context. Token costs grow linearly with conversation length.

## Why the parameter is called `checkpointer`

`create_agent` is built on LangGraph, which saves state by taking **checkpoints** — snapshots of everything the agent knows at a given moment. For a conversational agent that is the message history, but agents can track other things too (covered in later modules). The parameter is named `checkpointer` rather than `memory` because it is the general state-persistence mechanism; memory is what you experience when the saved state is a message history.

## Storage backends

All checkpointers are passed the same way via the `checkpointer` parameter — swapping backends requires no other code changes:

```python
# Development — in-process, lost on restart
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

# Local / embedded — survives restarts, single process
# pip install langgraph-checkpoint-sqlite
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# Production — multi-instance, durable
# pip install langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@host/db")

# High-throughput — fast reads, requires Redis 8+ or Redis Stack
# pip install langgraph-checkpoint-redis
from langgraph.checkpoint.redis import RedisSaver
with RedisSaver.from_conn_string("redis://localhost:6379") as checkpointer:
    checkpointer.setup()  # required on first use — creates indices
    agent = create_agent(model, checkpointer=checkpointer)

# MongoDB
# pip install langgraph-checkpoint-mongodb
from langgraph.checkpoint.mongodb import MongoDBSaver
with MongoDBSaver.from_conn_string("mongodb://localhost:27017", "mydb") as checkpointer:
    agent = create_agent(model, checkpointer=checkpointer)

# AWS (Bedrock AgentCore / DynamoDB / ElastiCache Valkey)
# pip install langgraph-checkpoint-aws
from langgraph_checkpoint_aws import AgentCoreMemorySaver
checkpointer = AgentCoreMemorySaver(memory_id="YOUR_MEMORY_ID", region_name="us-east-1")
agent = create_agent(model, checkpointer=checkpointer)
# config also accepts actor_id: {"configurable": {"thread_id": "1", "actor_id": "agent-1"}}
```

| Backend | Package | Persists | Best for |
|---|---|---|---|
| `InMemorySaver` | `langgraph` | No | Dev / testing |
| `SqliteSaver` | `langgraph-checkpoint-sqlite` | Yes | Local / embedded |
| `PostgresSaver` | `langgraph-checkpoint-postgres` | Yes | Production, multi-instance |
| `RedisSaver` | `langgraph-checkpoint-redis` | Yes | High-throughput |
| `MongoDBSaver` | `langgraph-checkpoint-mongodb` | Yes | MongoDB-native stacks |
| `AgentCoreMemorySaver` | `langgraph-checkpoint-aws` | Yes | AWS deployments (Bedrock/DynamoDB) |
| Managed | LangGraph Platform / LangSmith | Yes | Automatic, no config |

## Context management

Storage and what gets sent to the model are separate concerns. Even with `InMemorySaver`, you control what portion of history the model sees on each call.

**`trim_messages`** — keep only the most recent tokens:

```python
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    response["messages"],
    max_tokens=500,
    token_counter="approximate",
    strategy="last",        # keep most recent
    include_system=True,    # always keep SystemMessage
)
```

**`filter_messages`** — remove by type:

```python
from langchain_core.messages import filter_messages

# Remove all ToolMessages before sending to model
human_and_ai_only = filter_messages(
    response["messages"],
    exclude_types=["tool"],
)
```

Both return a plain `list[BaseMessage]` — pass it as `{"messages": trimmed}` on the next invoke.

Covered in depth in Module 3 (`3.2_managing_messages.ipynb`).

## Open questions

- How do you clear a thread's history (reset memory for a session)?
- How does `InMemorySaver` behave with tool calls — does it store `ToolMessage` entries too?
- What happens to memory when `recursion_limit` is hit?

## Related sources

- [[lc-foundations-foundational-models]] — `create_agent` basics
- [[lc-foundations-tools]] — tool-call message flow
- [[ch05-memory]] — full pedagogical chapter
