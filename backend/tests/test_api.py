"""Tests for the FastAPI API endpoints.

We build a minimal FastAPI app that mirrors the real endpoints but uses an
injected mock RAG system.  This avoids importing backend/app.py which mounts
static files from a directory that doesn't exist in the test environment.
"""

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional


# ---------------------------------------------------------------------------
# Pydantic models (duplicated from app.py to stay import-free)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


# ---------------------------------------------------------------------------
# Test app factory
# ---------------------------------------------------------------------------

def _create_test_app(rag_system: MagicMock) -> FastAPI:
    """Build a lightweight FastAPI app wired to the given mock RAG system."""
    test_app = FastAPI()

    @test_app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @test_app.delete("/api/session/{session_id}")
    async def delete_session(session_id: str):
        rag_system.session_manager.clear_session(session_id)
        return {"status": "ok"}

    @test_app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return test_app


@pytest.fixture
def client(mock_rag_system):
    """TestClient wired to a mock RAG system."""
    app = _create_test_app(mock_rag_system)
    return TestClient(app)


@pytest.fixture
def rag(mock_rag_system):
    """Shortcut to the underlying mock for assertions."""
    return mock_rag_system


# ===================================================================
# POST /api/query
# ===================================================================

class TestQueryEndpoint:
    def test_query_returns_answer_and_sources(self, client, rag):
        resp = client.post("/api/query", json={"query": "What is AI?"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["answer"] == "This is a test answer."
        assert data["sources"] == ["Intro to AI - Lesson 0"]
        assert data["session_id"] == "session_1"

    def test_query_creates_session_when_missing(self, client, rag):
        client.post("/api/query", json={"query": "hello"})
        rag.session_manager.create_session.assert_called_once()

    def test_query_uses_provided_session_id(self, client, rag):
        resp = client.post("/api/query", json={"query": "hello", "session_id": "my-session"})
        data = resp.json()
        assert data["session_id"] == "my-session"
        rag.session_manager.create_session.assert_not_called()
        rag.query.assert_called_once_with("hello", "my-session")

    def test_query_missing_body_returns_422(self, client):
        resp = client.post("/api/query", json={})
        assert resp.status_code == 422

    def test_query_empty_string_is_valid(self, client):
        resp = client.post("/api/query", json={"query": ""})
        assert resp.status_code == 200

    def test_query_internal_error_returns_500(self, client, rag):
        rag.query.side_effect = RuntimeError("boom")
        resp = client.post("/api/query", json={"query": "fail"})
        assert resp.status_code == 500
        assert "boom" in resp.json()["detail"]


# ===================================================================
# GET /api/courses
# ===================================================================

class TestCoursesEndpoint:
    def test_courses_returns_stats(self, client, rag):
        resp = client.get("/api/courses")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_courses"] == 1
        assert data["course_titles"] == ["Intro to AI"]

    def test_courses_internal_error_returns_500(self, client, rag):
        rag.get_course_analytics.side_effect = RuntimeError("db error")
        resp = client.get("/api/courses")
        assert resp.status_code == 500
        assert "db error" in resp.json()["detail"]


# ===================================================================
# DELETE /api/session/{session_id}
# ===================================================================

class TestSessionEndpoint:
    def test_delete_session_returns_ok(self, client, rag):
        resp = client.delete("/api/session/session_1")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
        rag.session_manager.clear_session.assert_called_once_with("session_1")
