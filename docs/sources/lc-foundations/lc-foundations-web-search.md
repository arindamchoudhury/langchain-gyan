---
name: lc-foundations-web-search
description: LangChain Module 1.2b — building a web search tool with Tavily and DDGS (DuckDuckGo), showing the knowledge cutoff problem, multi-turn tool calls, and comparing the two search providers
---

# Module 1.2b: Web Search

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 2)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `notebooks/module-1/1.2_web_search.ipynb`
> **Added:** 2026-05-30
> **Tags:** web-search, tavily, ddgs, duckduckgo, tool, training-cutoff, multi-turn-tool-calls
> **Type:** notebook / course lesson

> 📌 **Full explained chapter:** [[ch04-web-search]]

## Summary

Demonstrates the training-cutoff limitation of LLMs without web access, then fixes it by wrapping Tavily and DuckDuckGo search as `@tool` functions. Shows that the agent may issue multiple tool calls when initial results are ambiguous, and compares the two search providers' return structures.

## Key points

- Without web search, the model answers from training data and admits its cutoff date
- `TavilyClient().search(query)` returns a dict with a scored `results` list — LLM-optimised
- `DDGS` (formerly `duckduckgo-search`) requires no API key; returns `{title, href, body}` snippets
- With DDGS, the agent made **two** tool calls — first results were ambiguous, so it refined the query
- Tavily results are pre-scored and content-summarised; DDGS results are raw snippets
- `ToolMessage.content` is always a string — the dict/list return is `.toString()`-ed automatically

## Notes

### The problem: training cutoff

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model=model)

question = HumanMessage(content="How up to date is your training knowledge?")
response = agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# "My training data includes information up to May 2025.
#  If you need current news or live data, enable web search."
```

The model knows what it doesn't know — but without a tool, it can't do anything about it.

### Tavily web search tool

```python
from langchain.tools import tool
from typing import Dict, Any
from tavily import TavilyClient

tavily_client = TavilyClient()  # reads TAVILY_API_KEY from env

@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_client.search(query)

# Test directly
result = web_search.invoke("Who is the current mayor of San Francisco?")
```

Return structure:
```python
{
    "query": "Who is the current mayor of San Francisco?",
    "answer": None,
    "images": [],
    "results": [
        {"url": "https://...", "title": "...", "content": "...", "score": 0.888, "raw_content": None},
        ...   # 5 results by default, sorted by relevance score
    ],
    "response_time": 0.86,
    "request_id": "..."
}
```

### Tavily agent — single tool call

```python
agent = create_agent(model=model, tools=[web_search])
question = HumanMessage(content="Who is the current mayor of San Francisco?")
response = agent.invoke({"messages": [question]})
print(response["messages"][-1].content)
# "The current mayor of San Francisco is Daniel Lurie. He was sworn in as
#  the 46th mayor on January 8, 2025, after defeating incumbent London Breed."
```

Message flow: 4 messages — Human → AI(tool_call) → Tool → AI(final). One tool call was enough because Tavily results were high-quality and unambiguous.

### DuckDuckGo (DDGS) — free, no API key

```python
from ddgs import DDGS

@tool
def web_search_ddgs(query: str) -> str:
    """Search the web for information"""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    return str(results)
```

Return structure (list of dicts, stringified):
```python
[
    {"title": "...", "href": "https://...", "body": "..."},
    ...
]
```

### DDGS agent — two tool calls

With DDGS, the agent made **two** tool calls. The first results included old pages mentioning Gavin Newsom (stale snippets). The model recognised the ambiguity and issued a second, more specific query:

```
Tool call 1: "current mayor of San Francisco"
  → results mixed old/new, agent uncertain

Tool call 2: "Daniel Lurie mayor of San Francisco 2025"
  → clear confirmation, agent answers
```

Message flow: **6 messages** — Human → AI(tool_call 1) → Tool → AI(tool_call 2) → Tool → AI(final).

This is the ReAct loop naturally iterating: reason → act → observe → reason again.

## Tavily vs DDGS comparison

| | Tavily | DDGS |
|---|---|---|
| API key | Required (`TAVILY_API_KEY`) | None |
| Cost | Free tier, then paid | Free |
| Return type | `Dict` (structured, scored) | `list[dict]` (raw snippets) |
| Result quality | Pre-scored, LLM-optimised | Raw web snippets |
| Tool calls needed | 1 (usually) | 2 (notebook; no fixed cap) |
| Token usage | Lower (concise content) | Higher (raw snippets) |

## Open questions

- Can `TavilyClient` be configured for `include_answer=True` to get an AI-generated summary in the `answer` field?
- Does `max_results` on DDGS affect quality or just quantity of results?

## Related sources

- [[lc-foundations-tools]] — `@tool` decorator basics
- [[ch04-web-search]] — full pedagogical chapter
