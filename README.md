# LangChain Learning Notes

Personal learning space for LangChain, LangGraph, and AI agent development.

## What's here

- **[Book](docs/book/index.md)** — chapters written as I complete each module
- **[Learning Path](docs/learning-path.md)** — ordered courses and books with time estimates
- **[Research Notes](docs/sources/index.md)** — notes from individual lessons and books
- **[Reference](docs/reference/glossary.md)** — glossary and resources

## Progress

Currently on **Stage 1 — Foundation**: Introduction to LangChain - Python (LangChain Academy)

### Book chapters

| # | Topic | Key concepts |
|---|-------|--------------|
| 1 | Foundational Models | `init_chat_model`, `AIMessage`, streaming, Ollama |
| 2 | Prompting | `system_prompt`, few-shot, structured output, Pydantic |
| 3 | Tools | `@tool` decorator, tool-call message flow |
| 4 | Web Search | Tavily, DDGS, multi-turn tool calls |
| 5 | Short-Term Memory | `InMemorySaver`, `thread_id`, stateless vs stateful |
| 6 | Multimodal Messages | Content blocks, image/audio base64 |

## Running locally

```bash
docker compose up
```

The site is served via [Zensical](zensical.toml) and configured in `zensical.toml`.
