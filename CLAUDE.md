# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A RAG (Retrieval-Augmented Generation) chatbot that answers questions about course materials. It uses ChromaDB for vector storage, Anthropic Claude for AI generation, and a vanilla HTML/JS/CSS frontend served by FastAPI.

## Commands

```bash
# Install dependencies
uv sync

# Run the app (serves on http://localhost:8000)
./run.sh
# or manually:
cd backend && uv run uvicorn app:app --reload --port 8000
```

There are no tests or linting configured.

## Architecture

**Request flow:** Frontend (`/api/query`) → `app.py` → `RAGSystem.query()` → Claude API with tool calling → `CourseSearchTool` searches ChromaDB → Claude generates final answer from search results.

### Backend (`backend/`)

- **app.py** — FastAPI server. Mounts frontend as static files at `/`. Two API endpoints: `POST /api/query` (chat) and `GET /api/courses` (stats). On startup, auto-loads `.txt` files from `docs/` into the vector store.
- **rag_system.py** — Main orchestrator. Wires together all components and handles the query pipeline. Uses tool-based search (Claude decides when to call `search_course_content`).
- **vector_store.py** — ChromaDB wrapper with two collections: `course_catalog` (course metadata, titles as IDs) and `course_content` (chunked lesson text). Uses `all-MiniLM-L6-v2` sentence-transformers for embeddings.
- **document_processor.py** — Parses course `.txt` files with a specific format: header lines (`Course Title:`, `Course Link:`, `Course Instructor:`) followed by `Lesson N: Title` markers. Chunks text by sentence boundaries with configurable size/overlap.
- **ai_generator.py** — Anthropic API client. Implements a single-round tool-use loop: sends query with tools → if Claude calls a tool, executes it and sends results back for final response.
- **search_tools.py** — Tool abstraction layer. `Tool` ABC defines the interface; `CourseSearchTool` implements search with optional course/lesson filtering. `ToolManager` registers tools and provides definitions for Claude's tool calling.
- **session_manager.py** — In-memory conversation history per session (no persistence across restarts).
- **models.py** — Pydantic models: `Course`, `Lesson`, `CourseChunk`.
- **config.py** — Dataclass config loaded from `.env`. Key settings: `CHUNK_SIZE=800`, `CHUNK_OVERLAP=100`, `MAX_RESULTS=5`, `MAX_HISTORY=2`.

### Frontend (`frontend/`)

Vanilla HTML/JS/CSS chat interface. Uses `marked.js` for markdown rendering. Communicates via `/api/query` and `/api/courses`. Session state tracked client-side.

### Data (`docs/`)

Course transcript `.txt` files. Expected format:
```
Course Title: ...
Course Link: ...
Course Instructor: ...

Lesson 0: Introduction
Lesson Link: ...
<content>
```

## Environment

- Python 3.13, managed with `uv`
- Requires `ANTHROPIC_API_KEY` in `.env` (copy from `.env.example`)
- ChromaDB persists to `backend/chroma_db/` (gitignored)
- Default AI model: `claude-sonnet-4-20250514`
