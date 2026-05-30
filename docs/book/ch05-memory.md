# Chapter 5: Short-Term Memory — Giving Agents Conversation History

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 3)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.3_memory.ipynb`
> **Version:** langchain 1.3.2 · langgraph 1.2.2 (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- Why agents forget everything between calls by default
- How `InMemorySaver` adds conversation memory with a single parameter
- What `thread_id` does and why it matters for multi-user apps
- How memory is implemented — and what it costs in tokens
- When to use `InMemorySaver` vs production-grade checkpointers

---

## The problem this solves

A stateless agent is like a support rep with amnesia — every message starts a brand new conversation. Ask it your name, it greets you. Ask it your name again in the next call, it has no idea who you are. For any conversational application — a chatbot, an assistant, a tutoring agent — this is a fundamental problem. Short-term memory fixes it: the agent remembers what was said earlier in the same session.

---

## Core concept

LangGraph agents store their state as **checkpoints**. By default, no checkpointer is set — each `.invoke()` call starts from a blank state and discards everything at the end.

When you pass a `checkpointer`, LangGraph saves a checkpoint after every step. On the next `.invoke()`, it loads the previous checkpoint and continues from there. The mechanism is simple: the full message history is replayed into the model's context window on every call.

A `thread_id` identifies which conversation history to load. Think of it as a session ID — the same `thread_id` = the same conversation; a different `thread_id` = a fresh session. This lets one agent serve multiple independent users simultaneously.

```
invoke(thread_id="1")  → loads thread-1 history → runs → saves checkpoint
invoke(thread_id="1")  → loads thread-1 history (now longer) → runs → saves
invoke(thread_id="2")  → loads thread-2 history (empty) → runs → saves
```

---

## Code examples

### Example 1: The amnesia problem

```python
# langchain 1.3.2 · langgraph 1.2.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model)

# Turn 1 — agent responds correctly
response = agent.invoke({"messages": [HumanMessage(content="Hello my name is Seán and my favourite colour is green")]})
print(response["messages"][-1].content)
# "Hello Seán! Green is a wonderful colour..."

# Turn 2 — agent has no memory of turn 1
response = agent.invoke({"messages": [HumanMessage(content="What's my favourite colour?")]})
print(response["messages"][-1].content)
# "I don't know your favourite colour, since we've never met or spoken before."
```

Each `.invoke()` only sees the messages you pass. Turn 2 gets one `HumanMessage` — the agent has no way to answer.

### Example 2: Adding memory with InMemorySaver

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
print(response["messages"][-1].content)
# "Hello Seán! Green is a wonderful colour..."

# Turn 2 — agent remembers turn 1
response = agent.invoke(
    {"messages": [HumanMessage(content="What's my favourite colour?")]},
    config,
)
print(response["messages"][-1].content)
# "Based on what you told me earlier, your favourite colour is green. 😊"
```

Two changes from the stateless version:
1. Pass `InMemorySaver()` as the `checkpointer` parameter on `create_agent`
2. `config` with `thread_id` passed to every `.invoke()`

### Example 3: What response["messages"] looks like with memory

After turn 2, `response["messages"]` contains the **full conversation history**, not just the current exchange:

```python
from pprint import pprint
pprint(response["messages"])
# [
#   HumanMessage("Hello my name is Seán and my favourite colour is green"),
#   AIMessage("Hello Seán! Green is a wonderful colour..."),
#   HumanMessage("What's my favourite colour?"),
#   AIMessage("Based on what you told me earlier, your favourite colour is green.")
# ]
```

The checkpointer accumulated the full history. Each new `.invoke()` loads everything, appends the new messages, and returns the complete state.

### Example 4: Thread isolation — multiple users

Different `thread_id` values give independent conversation histories:

```python
config_a = {"configurable": {"thread_id": "user-alice"}}
config_b = {"configurable": {"thread_id": "user-bob"}}

agent.invoke({"messages": [HumanMessage("My name is Alice")]}, config_a)
agent.invoke({"messages": [HumanMessage("My name is Bob")]}, config_b)

# Alice's thread has no knowledge of Bob's messages and vice versa
response = agent.invoke({"messages": [HumanMessage("What's my name?")]}, config_a)
print(response["messages"][-1].content)  # "Your name is Alice"

response = agent.invoke({"messages": [HumanMessage("What's my name?")]}, config_b)
print(response["messages"][-1].content)  # "Your name is Bob"
```

### Example 5: The token cost of memory

Memory is implemented by replaying history — every turn sends the full accumulated context:

| Call | Memory | Input tokens |
|---|---|---|
| Turn 1 | Off | 16 |
| Turn 2 | Off | 10 ← only new question |
| Turn 1 | On | 16 |
| Turn 2 | On | 79 ← full history included |

These counts come directly from `response["messages"][-1].usage_metadata["input_tokens"]` — the actual counts reported by the DeepSeek API in the notebook output, not estimates. Turn 2 with memory uses 79 tokens instead of 10 because the entire previous exchange is included. Token costs grow with conversation length — a long session can accumulate thousands of tokens on every call.

---

## Other memory approaches

### Why the parameter is called `checkpointer`

`create_agent` is built on LangGraph, which saves state by taking **checkpoints** — snapshots of everything the agent knows at a given moment. For a conversational agent, that state is the message history. But agents can track other things too (covered in later modules), and the checkpointer persists all of it.

The parameter is named `checkpointer` rather than `memory` because it is the general state-persistence mechanism — memory is simply what you experience when that saved state happens to be a message history.

### Swapping the storage backend

Every checkpointer is passed the same way — swapping backends is a one-line change:

```python
# Local SQLite — survives restarts, no server needed
# pip install langgraph-checkpoint-sqlite
from langgraph.checkpoint.sqlite import SqliteSaver

agent = create_agent(model, checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))

# Production PostgreSQL
# pip install langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver

agent = create_agent(model, checkpointer=PostgresSaver.from_conn_string("postgresql://..."))

# High-throughput Redis (requires Redis 8+ or Redis Stack)
# pip install langgraph-checkpoint-redis
from langgraph.checkpoint.redis import RedisSaver

with RedisSaver.from_conn_string("redis://localhost:6379") as checkpointer:
    checkpointer.setup()  # required on first use — creates search indices
    agent = create_agent(model, checkpointer=checkpointer)
```

| Backend | Persists | Best for |
|---|---|---|
| `InMemorySaver` | No | Dev / testing |
| `SqliteSaver` | Yes | Local / single-process |
| `PostgresSaver` | Yes | Production, multi-instance |
| `RedisSaver` | Yes | High-throughput |
| `MongoDBSaver` | Yes | MongoDB-native stacks |
| `AgentCoreMemorySaver` | Yes | AWS (Bedrock/DynamoDB) |
| LangGraph Platform | Yes | Managed, no config needed |

### Controlling what the model sees

Storage and context are separate concerns. The checkpointer stores everything; you decide what fraction of that history to include in each call.

**`trim_messages`** — keep only the most recent N tokens:

```python
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    messages,
    max_tokens=500,
    token_counter="approximate",  # or pass a model for exact counts
    strategy="last",              # keep most recent
    include_system=True,          # preserve SystemMessage
)
agent.invoke({"messages": trimmed}, config)
```

**`filter_messages`** — remove messages by type:

```python
from langchain_core.messages import filter_messages

# Strip ToolMessages to reduce noise in long agentic conversations
clean = filter_messages(messages, exclude_types=["tool"])
agent.invoke({"messages": clean}, config)
```

Both return `list[BaseMessage]` — pass directly as the `messages` value. Module 3 covers these in depth.

---

## Best practices

- **Always pass `config` with `thread_id`** — if you forget, the checkpointer saves but can never retrieve (no key to look up). The agent will behave as if it has no memory.
- **Use `InMemorySaver` only for development** — data is lost when the process restarts. For production, use `PostgresSaver` from `langgraph-checkpoint-postgres`
- **Use unique `thread_id` values per user session** — UUIDs or user IDs work well. Reusing IDs across unrelated conversations will merge their histories
- **Monitor token growth in long conversations** — without a trimming strategy, a months-long conversation thread will eventually hit the model's context window limit. Module 3 covers managing long conversations
- **`MemorySaver` is an alias** — `from langgraph.checkpoint.memory import MemorySaver` works identically; `InMemorySaver` is the canonical name in current docs

---

## Common pitfalls

- **Forgetting `config` on subsequent calls** — if turn 1 passes `config` but turn 2 doesn't, turn 2 starts a new blank thread. The agent won't error; it just won't remember anything.

- **Sharing one `InMemorySaver` instance across agents** — `InMemorySaver()` is stateful. If you create two agents that share the same instance, their checkpoints are stored in the same dict and may conflict if thread IDs overlap.

- **Unbounded memory growth** — `InMemorySaver` never evicts old checkpoints. In a long-running dev session with many threads, it consumes increasing memory. Restart the process or implement periodic cleanup.

- **Context window overflow** — the full message history is sent on every call. A very long conversation will eventually exceed the model's context window (`context_length_exceeded` error). Use LangChain's message trimming utilities (covered in Module 3) to keep history within limits.

- **`InMemorySaver` in production** — data is lost on restart. Any open user sessions lose their history. Use `PostgresSaver` or deploy via LangSmith, which provides a managed checkpointer automatically.

---

## Exercises

1. **Recall** — What two things must you add to `create_agent` and `.invoke()` to enable short-term memory? What happens if you pass a different `thread_id` on the second call?

2. **Apply** — Start a three-turn conversation with memory enabled. After turn 3, print `len(response["messages"])` and the `input_tokens` from `response["messages"][-1].usage_metadata`. How do they compare to turn 1?

3. **Extend** — Build a simple multi-user chat: create two separate `thread_id` values, have each "user" send two messages, then ask each agent "what did I tell you?" Verify that Alice's agent doesn't know Bob's messages.

---

## Summary

- By default, `create_agent` is stateless — each `.invoke()` sees only the messages passed to it
- `InMemorySaver` adds a checkpointer that persists full conversation history in memory, keyed by `thread_id`
- `config = {"configurable": {"thread_id": "..."}}` must be passed on every `.invoke()` call
- Memory works by replaying the full history — `response["messages"]` grows with each turn, and so do input token costs
- `InMemorySaver` is for development only; use `PostgresSaver` in production
- The next chapter builds on this with **multimodal messages** — sending images and other media to agents
