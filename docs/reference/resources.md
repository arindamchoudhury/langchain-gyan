# Resources

| Title | URL | Notes |
|---|---|---|
| LangChain Academy | https://academy.langchain.com | Course platform |
| Course repo | https://github.com/langchain-ai/lca-lc-foundations | Clone with `git clone --depth 1` |
| Conda env file | `environment.yml` in repo root | `conda env create -f environment.yml` |
| OpenAI API Keys | https://platform.openai.com/api-keys | Required for course |
| Tavily | https://tavily.com | Required search API, generous free tier |
| uv docs | https://docs.astral.sh/uv | Recommended package manager |
| LangSmith | https://smith.langchain.com | Optional tracing/evaluation platform |
| LangSmith EU | https://eu.api.smith.langchain.com | EU instance endpoint |
| LangChain chat model providers | https://python.langchain.com/docs/integrations/chat | If substituting non-OpenAI models |
| @tool decorator reference | https://reference.langchain.com/python/langchain-core/tools/convert/tool | Full signature and parameter docs |
| Tavily Python SDK | https://docs.tavily.com/sdk/python/reference | TavilyClient.search() return structure |
| DDGS (DuckDuckGo) | https://pypi.org/project/duckduckgo-search/ | Free search, no API key, renamed from duckduckgo-search |
| Exa search (langchain-exa) | https://docs.langchain.com/oss/python/integrations/providers/exa_search | Neural search, ExaSearchResults tool |
| Google Custom Search | https://docs.langchain.com/oss/python/integrations/tools/google_search | GoogleSearchAPIWrapper, needs GOOGLE_API_KEY + GOOGLE_CSE_ID |
| Brave Search API | https://brave.com/search/api | REST API, no LangChain package, use custom @tool |
