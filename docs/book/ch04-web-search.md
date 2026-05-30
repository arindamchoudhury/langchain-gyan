# Chapter 4: Web Search — Connecting Agents to Live Data

> **Source:** [LangChain Academy — Foundation: Introduction to LangChain (Module 1, Lesson 2)](https://academy.langchain.com/courses/take/foundation-introduction-to-langchain-python)
> **Notebooks:** `1.2_web_search.ipynb`
> **Version:** langchain 1.3.2 · tavily-python · ddgs (May 2026)
> **Added:** 2026-05-30

---

## What you'll learn

- Why LLMs fail on questions about recent events — and how to fix it
- How to wrap Tavily and DuckDuckGo as `@tool` functions
- The structure of search results from each provider
- Why the agent sometimes makes multiple tool calls — and why that's expected
- How to choose between Tavily (API key) and DDGS (free) for your project

---

## The problem this solves

Every language model has a training cutoff — a date after which it knows nothing. Ask about a recent election, a new product launch, or today's weather and it either guesses or admits it doesn't know. For any application where accuracy and recency matter, this is unacceptable.

Web search tools solve this directly: the agent searches the live web, reads the results, and synthesises an answer grounded in current data. The model's job shifts from "recall from training" to "reason over search results."

---

## Core concept

A web search tool is just a `@tool`-decorated function that calls a search API. The model decides the query, your function runs the actual HTTP call, and the results come back as a `ToolMessage`. The model reads those results and writes the final answer — it never had to "know" anything; it just learned it from the search.

The training-cutoff problem disappears entirely for any topic the web covers, which is most topics.

```
User: "Who won the 2025 SF mayoral election?"
  → Model: "I need current info. Call web_search('SF mayor 2025')"
  → Tool: hits Tavily/DDGS, returns results
  → Model: reads results, answers: "Daniel Lurie, sworn in Jan 8 2025"
```

**One subtlety:** search results vary in quality. Tavily pre-scores and summarises content for LLMs. DuckDuckGo returns raw snippets that may include old or ambiguous pages. When results are ambiguous, the ReAct loop iterates — the model calls the tool a second time with a more precise query. This is not a bug; it's the agent reasoning correctly.

---

## Code examples

### Example 1: The training cutoff in action

```python
# langchain 1.3.2 (May 2026)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")
agent = create_agent(model=model)

response = agent.invoke({"messages": [HumanMessage(content="How up to date is your training knowledge?")]})
print(response["messages"][-1].content)
# "My training data includes information up to May 2025.
#  I don't have real-time browsing capabilities..."
```

The model is honest — it knows its limit. Now we fix it.

### Example 2: Tavily web search tool

Tavily returns structured, scored results optimised for LLMs. Requires a free API key (`TAVILY_API_KEY`).

```python
from langchain.tools import tool
from typing import Dict, Any
from tavily import TavilyClient

tavily_client = TavilyClient()  # reads TAVILY_API_KEY from env

@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_client.search(query)

# Test the tool directly before using in an agent
result = web_search.invoke("Who is the current mayor of San Francisco?")
# {
#   "query": "Who is the current mayor of San Francisco?",
#   "answer": None,
#   "images": [],
#   "results": [
#     {"url": "https://en.wikipedia.org/wiki/...", "title": "Mayor of San Francisco - Wikipedia",
#      "content": "Incumbent Daniel Lurie since January 8, 2025", "score": 0.888},
#     ...
#   ],
#   "response_time": 0.86
# }
```

### Example 3: Agent with Tavily — single tool call

```python
agent = create_agent(model=model, tools=[web_search])

response = agent.invoke({"messages": [HumanMessage(content="Who is the current mayor of San Francisco?")]})
print(response["messages"][-1].content)
# "The current mayor of San Francisco is Daniel Lurie. He was sworn in as the
#  46th mayor on January 8, 2025, after defeating incumbent London Breed."
```

Tavily's scored, clean results were unambiguous — the agent answered in one tool call (4 messages total).

### Example 4: DuckDuckGo (DDGS) — no API key needed

```python
from ddgs import DDGS

@tool
def web_search_ddgs(query: str) -> str:
    """Search the web for information"""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    return str(results)
# Returns: "[{'title': '...', 'href': 'https://...', 'body': '...'}, ...]"
```

The return type is `str` (the list stringified) — LangChain always passes a string to `ToolMessage.content`.

### Example 5: Agent with DDGS — two tool calls

```python
agent = create_agent(model=model, tools=[web_search_ddgs])

response = agent.invoke({"messages": [HumanMessage(content="Who is the current mayor of San Francisco?")]})

from pprint import pprint
pprint(response["messages"])
# [
#   HumanMessage('Who is the current mayor...'),
#   AIMessage('', tool_calls=[{'name': 'web_search_ddgs', 'args': {'query': 'current mayor of San Francisco'}}]),
#   ToolMessage('...results including old Gavin Newsom pages...'),
#   AIMessage('', tool_calls=[{'name': 'web_search_ddgs', 'args': {'query': 'Daniel Lurie mayor of San Francisco 2025'}}]),
#   ToolMessage('...clear Daniel Lurie confirmation...'),
#   AIMessage('The current mayor of San Francisco is Daniel Lurie...')
# ]
```

**6 messages, 2 tool calls.** The first DDGS results mixed current and stale pages — the model spotted the ambiguity (old results mentioned Gavin Newsom) and issued a more specific second query to confirm. This is the ReAct loop working as designed.

---

## Tavily vs DDGS

| | Tavily | DDGS |
|---|---|---|
| API key | Required | None |
| Cost | Free tier, then paid | Free forever |
| Result format | Structured dict with `score` | Raw `{title, href, body}` snippets |
| LLM-optimised | Yes — content pre-summarised | No — raw web snippets |
| Typical tool calls | 1 | 2 (notebook; no fixed cap) |
| Token consumption | Lower | Higher |
| Best for | Production, accuracy-critical | Development, no-key-needed |

Use Tavily when quality and reliability matter. Use DDGS for local development or projects where you can't use paid APIs.

---

## Other search providers

### Exa (`langchain-exa`)

Exa is a neural search engine built for AI — it understands semantic intent rather than just matching keywords. It ships as a pre-built `BaseTool`, so no `@tool` wrapper needed.

```python
# pip install langchain-exa
# EXA_API_KEY in .env
from langchain_exa import ExaSearchResults

exa_tool = ExaSearchResults(
    num_results=5,
    type="auto",          # "neural" | "keyword" | "auto"
)

agent = create_agent(model=model, tools=[exa_tool])
```

`ExaFindSimilarResults` is a second tool in the package — given a URL, it finds semantically similar pages. Useful for research tasks where you have a reference document and want more like it.

### Google Custom Search (`langchain-google-community`)

Uses the official Google Custom Search API. Requires two credentials: a Google API key and a Custom Search Engine ID (CSE ID).

```python
# pip install langchain-google-community
# GOOGLE_API_KEY and GOOGLE_CSE_ID in .env
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.tools import tool

search = GoogleSearchAPIWrapper(k=5)

@tool
def google_search(query: str) -> str:
    """Search Google for current information"""
    return search.run(query)

agent = create_agent(model=model, tools=[google_search])
```

`search.results(query, num_results)` returns structured dicts with `Snippet`, `Title`, and `Link` if you need to parse fields rather than pass raw text.

### Brave Search (custom `@tool`)

No dedicated LangChain package — Brave's search API is called directly. Requires a `BRAVE_SEARCH_API_KEY` from [brave.com/search/api](https://brave.com/search/api).

```python
import os, requests
from langchain.tools import tool

@tool
def brave_search(query: str) -> str:
    """Search the web using Brave Search"""
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"Accept": "application/json",
                 "X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"]},
        params={"q": query, "count": 5},
    )
    results = resp.json().get("web", {}).get("results", [])
    return str([{"title": r["title"], "url": r["url"], "description": r["description"]}
                for r in results])

agent = create_agent(model=model, tools=[brave_search])
```

Privacy-focused, no tracking, independent index. Free tier available.

### Full provider comparison

| Provider | Package | API key | Cost | Notes |
|---|---|---|---|---|
| Tavily | `tavily-python` | Yes | Free tier | LLM-optimised, scored results |
| DDGS | `ddgs` | No | Free | Raw snippets, may need 2 calls |
| Exa | `langchain-exa` | Yes | Free tier | Neural/semantic, pre-built tool |
| Google | `langchain-google-community` | Yes × 2 | Free tier | Google index, needs CSE ID |
| Brave | REST API | Yes | Free tier | Privacy-first, independent index |

For most projects: **Tavily in production, DDGS in development**. Add Exa when you need semantic similarity search. Google/Brave when you specifically need their index.

---

## Best practices

- **Test tools with `.invoke()` before attaching to an agent** — if `TavilyClient()` raises an auth error, you'll know immediately rather than debugging it inside an agent run
- **Return `str` from tools explicitly for DDGS** — LangChain stringifies anyway, but `str(results)` makes the intent clear and avoids surprises with custom serialisation
- **Add `include_answer=True` to Tavily for simple factual queries** — `TavilyClient().search(query, include_answer=True)` returns a pre-synthesised `answer` field, reducing the model's work
- **Keep `max_results` small** — 5 results is usually plenty. More results = more tokens in the ToolMessage = higher cost per call
- **Use a specific docstring** — "Search the web for information" is fine for a general tool, but if you have multiple tools (web search + database search), be more specific: "Search the live web for current news and facts"

---

## Common pitfalls

- **`TAVILY_API_KEY` not in environment** — `TavilyClient()` will raise an auth error. Make sure `load_dotenv()` runs before instantiating the client, and that `.env` contains the key.

- **DDGS rate limiting** — DuckDuckGo limits unauthenticated requests. Heavy usage will result in 202/429 responses. For production, use Tavily or another paid API.

- **Stale DDGS results triggering extra tool calls** — DuckDuckGo's index includes older pages. The agent may need 2 tool calls for time-sensitive queries. This is expected behaviour — but it adds latency and token cost. Tavily's scoring largely avoids this.

- **`duckduckgo-search` vs `ddgs`** — the package was renamed. `from ddgs import DDGS` is current. `from duckduckgo_search import DDGS` still works but prints a `RuntimeWarning` recommending migration.

- **`ToolMessage.content` is always a string** — if your tool returns a `dict` (like Tavily), LangChain converts it to a string. The model parses it from text. For Tavily this is fine; for complex nested objects, consider returning `json.dumps(result)` explicitly for more predictable formatting.

---

## Exercises

1. **Recall** — The DDGS agent made two tool calls but the Tavily agent only made one. What caused the agent to make a second call, and what does that tell you about DDGS result quality?

2. **Apply** — Add `include_answer=True` to the Tavily `client.search()` call. Run the same query and print `result["answer"]`. How does the pre-generated answer compare to what the agent synthesised itself?

3. **Extend** — Build a news agent with two tools: `search_news(query)` using Tavily with `search_depth="advanced"` and `topic="news"`, and `search_general(query)` for non-news facts. Ask the agent a question that should use news (e.g. "latest AI announcements this week") and one that should use general search. Does it pick the right tool each time?

---

## Summary

- Without web tools, agents are limited to training-data knowledge and admit their cutoff date
- `TavilyClient().search(query)` returns scored, LLM-optimised results; requires `TAVILY_API_KEY`
- `DDGS().text(query)` returns free raw snippets; no API key; install `ddgs` (not the old `duckduckgo-search`)
- The agent may make multiple tool calls when results are ambiguous — this is the ReAct loop iterating correctly
- Tavily needs 1 tool call in most cases; DDGS may need 2 for recent or specific queries
- The next chapter covers **short-term memory** — giving the agent the ability to remember earlier turns in a conversation
