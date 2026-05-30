# Learning Path Skill — Design Spec

**Date:** 2026-05-30
**Status:** Approved

---

## Overview

A generic Claude Code skill that, for any learning topic, does three things automatically:

1. **Researches** books and courses on the topic, analyses their structure, and auto-generates a topic-specific book writing skill
2. **Creates** a structured learning path (ordered books + courses with time estimates)
3. **Writes a book chapter by chapter** as the user completes each course module or book chapter — blending, validating, and keeping content current with the latest release of the technology

---

## Folder Structure

Each topic gets its own isolated workspace:

```
C:\opt\learn\<topic-slug>\
├── <course-repo>\              ← cloned repos (managed by user)
└── notes\                      ← everything the skill manages
    ├── zensical.toml
    ├── serve.py
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .gitignore
    ├── .env                    ← SITE_EMAIL, SITE_PASSWORD for fetch script; plus any topic API keys
    ├── docs\
    │   ├── index.md            ← book home + site hub
    │   ├── learning-path.md    ← ordered books + courses
    │   ├── book\
    │   │   ├── index.md        ← auto-maintained book TOC
    │   │   └── ch<NN>-<slug>.md  ← one chapter per completed module
    │   ├── sources\            ← research notes per book/course
    │   │   └── index.md
    │   └── reference\
    │       ├── glossary.md
    │       └── resources.md
    ├── cache\
    │   ├── web\                ← fetched page text
    │   └── search\             ← verified fact cache (reused across sessions)
    └── scripts\
        └── fetch_page.py       ← Cloudflare-bypass fetch (nodriver)
```

**Topic slug examples:** `ai-agents`, `databricks`, `langchain`, `python`, `mlops`

---

## Phase Detection

The skill detects which phase to run based on file state:

| Condition | Phase to run |
|---|---|
| `notes\` doesn't exist OR `docs\learning-path.md` missing | Phase 1 → Phase 2 |
| `learning-path.md` exists + user says "I finished X" | Phase 3 |
| `learning-path.md` exists + no trigger | Show current status |

---

## Phase 1 — Research & Scaffold

**Goal:** Understand how the topic is taught, scaffold the notes site, create a topic book skill.

### 1.1 Research books
- Web search: `"best books on <topic> 2026 table of contents"`
- Web search: `"<topic> book site:oreilly.com OR site:manning.com OR site:packtpub.com 2024 2025 2026"`
- For each top 3–5 books: fetch the TOC page, extract chapter list
- Identify the common progression arc (what comes first, what's advanced)

### 1.2 Research courses
- Web search: `"best <topic> courses 2026 Udemy Coursera official"`
- Include official academies (LangChain Academy, Databricks Academy, etc.)
- Note module structure where available

### 1.3 Validate with official docs
- Fetch the official documentation home page for the technology
- Note current stable version
- Flag any books/courses that target significantly older versions

### 1.4 Scaffold notes folder
- Copy the proven structure from `C:\opt\learn\langchain\notes`:
  - `zensical.toml`, `serve.py`, `Dockerfile`, `docker-compose.yml`, `.gitignore`
  - `scripts\fetch_page.py` (nodriver Cloudflare bypass, reads `.env` for credentials)
  - Empty `docs\`, `cache\web\`, `cache\search\`
- Customise: site name, author from `.env`

### 1.5 Auto-generate topic book skill
- Create `~/.claude/skills/<topic>-book/SKILL.md`
- Content based on research: proven chapter arc, code standards for the tech, key patterns, current package versions, anti-patterns
- Follows the same structure as `langchain-book` skill

### 1.6 Write initial docs
- `docs\index.md` — site home
- `docs\sources\index.md` — empty source log
- `docs\reference\glossary.md` — empty
- `docs\reference\resources.md` — links found during research

---

## Phase 2 — Learning Path

**Goal:** Write `docs\learning-path.md` with a clear, opinionated progression.

### Format

```markdown
# Learning Path: <Topic>

## Prerequisites
- ...

## The Path

### Stage 1: Foundations (~X hours)
**Course/Book:** [Name](url)
**Focus:** what to pay attention to
**Skip:** what's optional or dated

### Stage 2: Core Concepts (~X hours)
...

### Stage N: Production / Advanced (~X hours)
...

## Quick Reference
| Resource | Type | Level | Hours | Priority |
|---|---|---|---|---|
```

### Rules
- Order by concept dependency, not by publisher prestige
- Mark each resource as: Essential / Recommended / Optional
- Include official docs as a resource (always)
- Flag resources that target older versions with a 📌 version note

---

## Phase 3 — Book Writing

**Triggered by:** User says "I finished [Module X / Chapter Y] of [course/book]"

### 3.1 Validate before writing
1. Check `cache\search\` — grep for the topic being covered
2. Web-search the official docs for the current API/version
3. Save new verified findings to `cache\search\<slug>.md`
4. Note the current stable version — add a version callout if it differs from what the course taught

### 3.2 Determine chapter action

| Situation | Action |
|---|---|
| Topic is entirely new | Create new `ch<NN>-<slug>.md` |
| Topic already covered in an existing chapter | Blend into existing chapter |
| Topic contradicts existing content | Add both framings + explanation |

**Blending rules (never rewrite, always blend):**
- Read the full existing chapter before touching it
- Add new content at the logical insertion point, not always at the end
- When two sources frame the same concept differently, present both: *"Lens 1 — ... · Lens 2 — ..."*
- Never drop existing content silently — every prior framing stays, new context added around it
- Call out contradictions explicitly: *"Unlike [earlier source] which says X, [new source] argues Y because..."*

### 3.3 Chapter structure
Each chapter follows the topic book skill's template (generated in Phase 1). Minimum sections:

```markdown
# Chapter N: <Title>

> **Source:** [Course/Book name — Module/Chapter title]
> **Covers:** <topic slug>
> **Version:** <tech version this was taught on>

## What you'll learn
## The problem this solves
## Core concept
## Code examples        ← always complete, always runnable
## Common pitfalls
## Exercises            ← recall / apply / extend
## Summary
```

### 3.4 Keep book current
- If the version taught is older than the current stable release, add:
  > 📌 **Version note:** This was taught on v<X>. Current stable is v<Y> as of <date>. API differences: ...
- When updating an existing chapter with newer info, update the version note rather than adding a second one

### 3.5 Sync nav
After every chapter write/update:
- Update `docs\book\index.md` TOC entry
- Update `zensical.toml` nav under the Book group

---

## Skill File Structure

```
~/.claude/skills/learning-path/
├── SKILL.md                    ← orchestrator (phase detection, delegates to refs)
└── references/
    ├── phase1-research.md      ← research instructions, scaffold template
    ├── phase2-path.md          ← learning path format + writing rules
    └── phase3-book.md          ← chapter writing, blending, validation rules
```

Auto-generated at runtime per topic:
```
~/.claude/skills/<topic>-book/
└── SKILL.md
```

---

## Content Integrity Principles

These apply to every chapter write and every update:

1. **Validate, never assume** — web-search or fetch official docs before writing version-specific facts
2. **Blend, never overwrite** — new learning adds to existing chapters, never replaces silently
3. **Always current** — reflect the newest stable release; add version callouts when course material is behind
4. **Contradictions are valuable** — when two sources disagree, capture both framings and explain the difference
5. **Cache verified facts** — save search results to `cache\search\` so the same fact is never looked up twice

---

## Auto-Generated Topic Book Skill Template

The `<topic>-book` skill generated in Phase 1 always includes:

- Proven chapter arc (derived from TOC research)
- Code standards for the technology (current version imports, patterns)
- Standard chapter template (same as above)
- Current package versions (verified at generation time)
- Key patterns every book on the topic covers
- Anti-patterns to avoid

---

## Out of Scope

- Managing course enrollments or downloads
- Video transcription
- Generating quizzes or flashcards
- PDF extraction (handled separately by research-notes skill if needed)
