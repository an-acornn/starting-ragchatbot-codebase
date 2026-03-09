"""Shared fixtures for RAG system tests."""

import pytest
from unittest.mock import MagicMock, patch

from models import Course, Lesson, CourseChunk
from config import Config


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_COURSE = Course(
    title="Intro to AI",
    course_link="https://example.com/ai",
    instructor="Dr. Smith",
    lessons=[
        Lesson(lesson_number=0, title="Introduction", lesson_link="https://example.com/ai/0"),
        Lesson(lesson_number=1, title="Neural Networks", lesson_link="https://example.com/ai/1"),
    ],
)

SAMPLE_CHUNKS = [
    CourseChunk(content="AI is transforming the world.", course_title="Intro to AI", lesson_number=0, chunk_index=0),
    CourseChunk(content="Neural networks mimic the brain.", course_title="Intro to AI", lesson_number=1, chunk_index=1),
]


@pytest.fixture
def sample_course():
    return SAMPLE_COURSE


@pytest.fixture
def sample_chunks():
    return SAMPLE_CHUNKS


# ---------------------------------------------------------------------------
# Config fixture (no .env required)
# ---------------------------------------------------------------------------

@pytest.fixture
def test_config():
    return Config(
        ANTHROPIC_API_KEY="test-key-not-real",
        ANTHROPIC_MODEL="claude-sonnet-4-20250514",
        CHUNK_SIZE=800,
        CHUNK_OVERLAP=100,
        MAX_RESULTS=5,
        MAX_HISTORY=2,
    )


# ---------------------------------------------------------------------------
# Mock RAG system
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rag_system():
    """A MagicMock standing in for RAGSystem with sensible defaults."""
    rag = MagicMock()
    rag.query.return_value = ("This is a test answer.", ["Intro to AI - Lesson 0"])
    rag.get_course_analytics.return_value = {
        "total_courses": 1,
        "course_titles": ["Intro to AI"],
    }
    rag.session_manager.create_session.return_value = "session_1"
    return rag
