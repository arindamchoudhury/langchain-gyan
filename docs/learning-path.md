# Learning Path: LangChain & AI Agents

> **Last updated:** 2026-05-30
> **Current stable versions:** langchain 1.3.2 · langchain-core 1.4.0 · langgraph 1.2.2 · langsmith 0.8.6

---

## Prerequisites

- Python (functions, classes, async/await basics)
- Basic understanding of what an API is and how to call one
- Familiarity with virtual environments and pip/conda
- No prior LLM or AI experience required

---

## The Path

### Stage 1: LangChain Foundations (~12 hours total)

#### Foundation: Introduction to LangChain - Python ⭐ CURRENTLY HERE
- **Type:** Official course
- **URL:** https://academy.langchain.com/courses/foundation-introduction-to-langchain-python
- **Priority:** Essential
- **Time:** ~8 hours (3 modules + projects)
- **Focus:** Module 1 (agents, tools, memory), Module 2 (MCP, multi-agent), Module 3 (middleware, HITL, dynamic agents)
- **Skip:** Nothing — this is the official starting point

#### LangChain Official Docs — Python Quickstart
- **Type:** Official docs
- **URL:** https://docs.langchain.com/oss/python
- **Priority:** Essential (reference alongside the course)
- **Time:** ~2 hours to read through, then reference as needed
- **Focus:** Current API patterns, `init_chat_model`, LCEL/Runnable interface
- **Skip:** Integrations catalog — consult only when you need a specific integration

#### Learning LangChain — Oshin & Campos (O'Reilly, 2025)
- **Type:** Book
- **URL:** https://www.oreilly.com/library/view/learning-langchain/9781098167271/
- **Priority:** Essential
- **Time:** ~20 hours
- **Focus:** Ch 1–5 (LLMs, prompts, output parsers, LCEL, chains), Ch 6–7 (embeddings, agents)
- **Skip:** Nothing in the core chapters — this is the most current O'Reilly book on LangChain 1.x

---

### Stage 2: Agents & RAG (~15 hours total)

#### Foundation: Introduction to LangGraph - Python
- **Type:** Official course
- **URL:** https://academy.langchain.com/courses/intro-to-langgraph
- **Priority:** Essential
- **Time:** ~8 hours (6 modules, 55 lessons)
- **Focus:** Module 1 (state/nodes/edges/agent), Module 2 (state reducers, memory), Module 3 (HITL), Module 4 (parallelization, map-reduce), Module 5 (long-term memory), Module 6 (deployment)
- **Skip:** Nothing — this is the definitive LangGraph course

#### LangChain Academy: LangGraph Essentials Quickstart
- **Type:** Official quickstart
- **URL:** https://academy.langchain.com/courses/langgraph-essentials-python
- **Priority:** Recommended (do after Introduction to LangGraph as a fast consolidation)
- **Time:** ~2 hours
- **Focus:** Building a complete email workflow as a practical capstone
- **Skip:** Can skip if Introduction to LangGraph already covered the concepts clearly

#### Generative AI with LangChain 2nd Ed — Auffarth & Kuligin (Packt, 2025)
- **Type:** Book
- **URL:** https://www.packtpub.com/en-us/product/generative-ai-with-langchain-9781837022007
- **Priority:** Recommended
- **Time:** ~20 hours
- **Focus:** Ch 3 (LangGraph workflows), Ch 4 (RAG), Ch 5–6 (agents, multi-agent), Ch 8 (evaluation)
- **Skip:** Ch 1–2 if Stage 1 is done; Ch 10 (future of models) is speculative

---

### Stage 3: Production & Observability (~10 hours total)

#### Foundation: Monitoring Production Agents
- **Type:** Official course
- **URL:** https://academy.langchain.com/courses/foundation-monitoring-production-agents
- **Priority:** Essential
- **Time:** ~4 hours
- **Focus:** LangSmith tracing, cost tracking, latency analysis, quality metrics
- **Skip:** Nothing

#### Foundation: Building Reliable Agents
- **Type:** Official course
- **URL:** https://academy.langchain.com/courses/foundation-building-reliable-agents
- **Priority:** Essential
- **Time:** ~4 hours
- **Focus:** Iterative improvement cycles, LangSmith evaluation, moving from PoC to production
- **Skip:** Nothing

#### Foundation: Introduction to LangSmith Deployment
- **Type:** Official course
- **URL:** https://academy.langchain.com/courses/foundation-intro-to-langsmith-deployment
- **Priority:** Recommended
- **Time:** ~2 hours
- **Focus:** Deploying and managing agents via LangSmith
- **Skip:** Can defer until you have an agent ready to deploy

---

### Stage 4: Advanced — Multi-Agent & MCP (~15 hours total)

#### Project: Deep Research with LangGraph
- **Type:** Official project course
- **URL:** https://academy.langchain.com/courses/deep-research-with-langgraph
- **Priority:** Essential
- **Time:** ~5 hours
- **Focus:** Multi-agent orchestration, subgraph patterns, real-world research pipeline

#### Project: Ambient Agents with LangGraph
- **Type:** Official project course
- **URL:** https://academy.langchain.com/courses/ambient-agents
- **Priority:** Recommended
- **Time:** ~5 hours
- **Focus:** Building a background email assistant; event-driven agent patterns

#### Project: Deep Agents
- **Type:** Official project course
- **URL:** https://academy.langchain.com/courses/deep-agents-with-langgraph
- **Priority:** Recommended
- **Time:** ~5 hours
- **Focus:** Long-running, complex agentic tasks

#### AI Agents and Applications — Infante (Manning, 2026)
- **Type:** Book
- **URL:** https://www.manning.com/books/ai-agents-and-applications
- **Priority:** Recommended
- **Time:** ~20 hours
- **Focus:** MCP integration, multi-agent systems with LangGraph, advanced RAG patterns
- **Skip:** Nothing — strong on MCP which other resources cover less deeply

---

### Stage 5: Supplementary Deep Dives (pick based on interest)

#### The Complete LangChain, LangGraph & LangSmith Course — Udemy
- **Type:** Video course
- **URL:** https://www.udemy.com/course/the-complete-langchain-langgraph-langsmith-course/
- **Priority:** Optional (good if you prefer video over books for LCEL + LangGraph)
- **Time:** ~12 hours
- **Focus:** LCEL orchestration, LangGraph state machines, LangSmith monitoring
- **Skip:** Sections overlapping with Academy courses already completed

#### LangChain — Agentic AI Engineering (Udemy, re-recorded 2026)
- **Type:** Video course
- **URL:** https://www.udemy.com/course/langchain/
- **Priority:** Optional
- **Time:** ~15 hours
- **Focus:** Production agent patterns, useful if you want a different teaching style
- **Skip:** Foundation sections already covered by Academy courses

---

## Quick Reference

| Resource | Type | Priority | ~Hours | Version |
|---|---|---|---|---|
| [LangChain Academy: Intro to LangChain](https://academy.langchain.com/courses/foundation-introduction-to-langchain-python) | Official course | Essential | 8 | 1.x |
| [LangChain Docs](https://docs.langchain.com/oss/python) | Official docs | Essential | 2+ ref | 1.3.2 |
| [Learning LangChain (O'Reilly)](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Book | Essential | 20 | 1.x |
| [LangChain Academy: Intro to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | Official course | Essential | 8 | 1.2.2 |
| [LangChain Academy: Monitoring Production Agents](https://academy.langchain.com/courses/foundation-monitoring-production-agents) | Official course | Essential | 4 | current |
| [LangChain Academy: Building Reliable Agents](https://academy.langchain.com/courses/foundation-building-reliable-agents) | Official course | Essential | 4 | current |
| [Generative AI with LangChain 2nd Ed](https://www.packtpub.com/en-us/product/generative-ai-with-langchain-9781837022007) | Book | Recommended | 20 | 1.x |
| [Project: Deep Research](https://academy.langchain.com/courses/deep-research-with-langgraph) | Official project | Essential | 5 | current |
| [AI Agents and Applications (Manning)](https://www.manning.com/books/ai-agents-and-applications) | Book | Recommended | 20 | current |
| [Project: Ambient Agents](https://academy.langchain.com/courses/ambient-agents) | Official project | Recommended | 5 | current |
| [Project: Deep Agents](https://academy.langchain.com/courses/deep-agents-with-langgraph) | Official project | Recommended | 5 | current |

**Total Essential:** ~52 hours
**Total including Recommended:** ~92 hours

---

## What to build as you learn

- **After Stage 1:** A conversational Q&A bot over your own documents (RAG)
- **After Stage 2:** A research agent that uses Tavily to answer questions and cites sources
- **After Stage 3:** Deploy your Stage 2 agent with LangSmith monitoring
- **After Stage 4:** A multi-agent email assistant (supervisor + research + draft agents)
- **After Stage 5:** A production-ready agent of your choosing with full observability
