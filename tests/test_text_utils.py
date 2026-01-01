import pytest
from src.shared.utils.text_utils import chunk_text

def test_chunk_text_small():
    text = "This is a small text."
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_text_paragraphs():
    # Two paragraphs, total length > max_chars
    p1 = "x" * 60
    p2 = "y" * 60
    text = f"{p1}\n\n{p2}"
    
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) == 2
    assert chunks[0].strip() == p1
    assert chunks[1].strip() == p2

def test_chunk_text_long_line():
    # One long line that needs splitting
    text = "a" * 150
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) == 2
    assert len(chunks[0]) == 100
    assert len(chunks[1]) == 50

def test_chunk_text_empty():
    assert chunk_text("") == []
