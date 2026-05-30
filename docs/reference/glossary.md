# Glossary

| Term | Definition | Source |
|---|---|---|
| init_chat_model | LangChain 1.x factory function that loads any chat model via a unified interface. Accepts `"provider:model"` shorthand or infers provider from model name. | [[lc-foundations-foundational-models]] |
| AIMessage | LangChain object representing a model response. Key fields: `.content` (text), `.usage_metadata` (normalised token counts), `.response_metadata` (provider-specific details). | [[lc-foundations-foundational-models]] |
| HumanMessage | LangChain message type representing user input. Passed in the `messages` list when invoking a model or agent. | [[lc-foundations-foundational-models]] |
| usage_metadata | Normalised token count dict on `AIMessage` — consistent across all providers: `input_tokens`, `output_tokens`, `total_tokens`. | [[lc-foundations-foundational-models]] |
| response_metadata | Provider-specific metadata dict on `AIMessage` — structure varies by provider. Contains model name, finish reason, raw token counts. | [[lc-foundations-foundational-models]] |
| temperature | Model parameter controlling output randomness. 0.0 = deterministic, 1.0 = creative/random. | [[lc-foundations-foundational-models]] |
| create_agent | LangChain 1.x function that builds a pre-compiled ReAct agent (LangGraph state graph). Takes `{"messages": [...]}` input, returns same. | [[lc-foundations-foundational-models]] |
| ReAct | Reasoning + Acting — the agent loop pattern: model reasons → calls tools → observes results → repeats until done. | [[lc-foundations-foundational-models]] |
| ChatOllama | LangChain integration for Ollama local models. No API key needed. Identical invoke/stream interface to cloud providers. | [[lc-foundations-foundational-models]] |
| stream_mode="messages" | `agent.stream()` parameter that yields `(AIMessageChunk, metadata)` per token. `metadata` includes `langgraph_node`. | [[lc-foundations-foundational-models]] |
| uv | Fast Python package and project manager from Astral. Handles Python version selection, virtual environments, and dependency installation. Recommended tool for this course. | [[lc-foundations-getting-set-up]] |
| LangSmith | LangChain's platform for tracing, evaluating, and monitoring LLM applications. Optional for this course but enables observability of agent runs. | [[lc-foundations-getting-set-up]] |
| Tavily | Search API that returns results in an LLM-friendly format. Used in the course for web search tools. Has a generous free tier. | [[lc-foundations-getting-set-up]] |
| LangGraph Studio | Visual development UI for LangGraph agents. Run locally with `langgraph dev` for modules 1 and 3. | [[lc-foundations-getting-set-up]] |
| gpt-5-nano | OpenAI model used as the primary model in this course. Very inexpensive. Invoked via `init_chat_model("gpt-5-nano")`. Superseded by `gpt-5.4-nano` (March 2026, $0.20/1M input tokens) but still valid. | [[lc-foundations-getting-set-up]] |
| DuckDuckGoSearchRun | LangChain tool from `langchain-community` providing web search with no API key. ⚠️ `langchain-community` is being deprecated — use the `ddgs` package with a custom `@tool` wrapper instead. | [[lc-foundations-getting-set-up]] |
| keep_alive | `ChatOllama` parameter controlling how long a model stays loaded in VRAM after the last request. Default: 5 minutes. Set to `"1h"` or `-1` (never unload). | [[lc-foundations-getting-set-up]] |
| think | `ChatOllama` kwarg passed directly to the Ollama API. `think=False` disables thinking/reasoning mode on Qwen3 models. Equivalent to LangChain's `reasoning=False`. | [[lc-foundations-foundational-models]] |
| reasoning (ChatOllama) | LangChain-documented parameter on `ChatOllama`. `reasoning=False` disables thinking mode; `reasoning=True` captures reasoning in `additional_kwargs["reasoning_content"]`. | [[lc-foundations-foundational-models]] |
| thinking mode | Qwen3 behaviour where the model reasons internally before answering. Enabled by default. Streaming chunks during reasoning have `content=""`. Disable with `think=False`. | [[lc-foundations-foundational-models]] |
| system_prompt | Parameter on `create_agent`. String prepended as a `SystemMessage` before every invocation. Shapes the agent's persona, tone, constraints, and output format. | [[lc-foundations-prompting]] |
| few-shot prompting | Technique of embedding input→output examples directly in the system prompt. The model learns the output style from the examples and applies it to new inputs. | [[lc-foundations-prompting]] |
| structured output | Technique using `response_format=PydanticModel` on `create_agent` to get a validated typed Python object back in `response["structured_response"]`. | [[lc-foundations-prompting]] |
| response_format | Parameter on `create_agent`. Accepts a Pydantic BaseModel class, TypedDict, or strategy. Forces the model to return data matching the schema; result in `response["structured_response"]`. | [[lc-foundations-prompting]] |
| structured_response | Key added to `agent.invoke()` output when `response_format` is set. Contains the validated Pydantic instance (or dict). Absent if `response_format` not set. | [[lc-foundations-prompting]] |
| BaseModel (Pydantic) | Base class for defining structured output schemas in Python. Fields with type annotations define what the model must return. | [[lc-foundations-prompting]] |
| num_ctx | `ChatOllama` parameter setting the context window size in tokens. Default 16 384 (~1.6 GB KV cache). Lower to `4096` to save VRAM on smaller GPUs. | [[lc-foundations-getting-set-up]] |
| uvx | Tool runner included with `uv`. Used in Module 2, Lesson 1 to run the MCP server. | [[lc-foundations-getting-set-up]] |
| @tool | Decorator from `langchain.tools` that wraps a Python function as a `BaseTool`. Infers input schema from type annotations; description from docstring or `description=` arg. | [[lc-foundations-tools]] |
| BaseTool | Base class for all LangChain tools. `@tool` returns a `BaseTool` instance. Has `.invoke()`, `.name`, `.description`, and `.args` attributes. | [[lc-foundations-tools]] |
| ToolMessage | LangChain message type carrying a tool's return value back to the model. Matched to the originating `AIMessage.tool_calls` entry via `tool_call_id`. | [[lc-foundations-tools]] |
| tool_calls | List on `AIMessage` populated when the model decides to call tools. Each entry: `{'name': str, 'args': dict, 'id': str, 'type': 'tool_call'}`. Content is empty when tool_calls is present. | [[lc-foundations-tools]] |
| return_direct | `@tool` parameter. When `True`, the tool's result is returned immediately as the agent's final answer, skipping the final LLM call. | [[lc-foundations-tools]] |
| TavilyClient | Python client for the Tavily search API. `TavilyClient().search(query)` returns a dict with `results` list (url, title, content, score). Requires `TAVILY_API_KEY`. | [[lc-foundations-web-search]] |
| DDGS | DuckDuckGo search Python library (package: `ddgs`, formerly `duckduckgo-search`). No API key needed. `DDGS().text(query, max_results=5)` returns `[{title, href, body}]`. | [[lc-foundations-web-search]] |
| training cutoff | The date after which a model's training data ends. Models have no knowledge of events after this date without external tools like web search. | [[lc-foundations-web-search]] |
| InMemorySaver | LangGraph checkpointer that stores conversation history in memory (`defaultdict`), keyed by `thread_id`. For development only — data lost on restart. Alias: `MemorySaver`. | [[lc-foundations-memory]] |
| thread_id | Key passed in `config = {"configurable": {"thread_id": "..."}}` to identify a conversation thread. Same ID = same history; different ID = fresh session. | [[lc-foundations-memory]] |
| checkpointer | Parameter on `create_agent` (and LangGraph graphs) that persists state between `.invoke()` calls. `InMemorySaver` for dev; `PostgresSaver` for production. | [[lc-foundations-memory]] |
| PostgresSaver | Production-grade LangGraph checkpointer from `langgraph-checkpoint-postgres`. Persists conversation history to a PostgreSQL database across restarts. | [[lc-foundations-memory]] |
| SqliteSaver | LangGraph checkpointer from `langgraph-checkpoint-sqlite`. Persists to a local SQLite file — survives restarts, no server needed. Good for single-process local apps. | [[lc-foundations-memory]] |
| RedisSaver | LangGraph checkpointer from `langgraph-checkpoint-redis`. Stores checkpoints in Redis. Requires `.setup()` on first use. Needs Redis 8+ or Redis Stack. | [[lc-foundations-memory]] |
| content blocks | List format for `HumanMessage.content`. Each block is a dict with `type` and type-specific fields. Enables multimodal messages by mixing text, image, and audio blocks. | [[lc-foundations-multimodal]] |
| memoryview | Python type returned by `ipywidgets.FileUpload` for uploaded file content. Must be converted to `bytes` before base64 encoding: `bytes(uploaded_file["content"])`. | [[lc-foundations-multimodal]] |
| gpt-4o-audio-preview | OpenAI model required for audio input. `gpt-5-nano` does not process audio. | [[lc-foundations-multimodal]] |
| MongoDBSaver | LangGraph checkpointer from `langgraph-checkpoint-mongodb`. Persists to MongoDB. `MongoDBSaver.from_conn_string(uri, db_name)`. | [[lc-foundations-memory]] |
| AgentCoreMemorySaver | LangGraph checkpointer from `langgraph-checkpoint-aws`. Uses Bedrock AgentCore / DynamoDB / ElastiCache Valkey. For AWS-native deployments. | [[lc-foundations-memory]] |
| trim_messages | `langchain_core.messages` utility. Trims a message list to fit within `max_tokens`. Parameters: `strategy` ("last"/"first"), `include_system`, `token_counter`. | [[lc-foundations-memory]] |
| filter_messages | `langchain_core.messages` utility. Filters a message list by type, name, or id. E.g. `exclude_types=["tool"]` strips all ToolMessages. | [[lc-foundations-memory]] |
| ExaSearchResults | Pre-built `BaseTool` from `langchain-exa`. Neural/semantic search. Parameters: `num_results`, `type` ("neural"/"keyword"/"auto"). Requires `EXA_API_KEY`. | [[ch04-web-search]] |
| ExaFindSimilarResults | Pre-built `BaseTool` from `langchain-exa`. Given a URL, finds semantically similar pages. | [[ch04-web-search]] |
| GoogleSearchAPIWrapper | Class from `langchain-google-community`. Wraps Google Custom Search API. Requires `GOOGLE_API_KEY` + `GOOGLE_CSE_ID`. Not itself a `BaseTool` — wrap with `@tool`. | [[ch04-web-search]] |
