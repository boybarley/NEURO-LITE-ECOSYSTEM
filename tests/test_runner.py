#!/usr/bin/env python3
import sys
import os
import time
import sqlite3

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'developer_tools'))

from emotional_state import EmotionalAnalyzer, EmotionalState
from rag_engine import RAGEngine
from context_manager import ContextManager
from post_processor import PostProcessor
from validate_data import DataValidator

def test_emotional_analyzer():
    print("[TEST] Emotional Analyzer...")
    analyzer = EmotionalAnalyzer()
    
    # Test Concern
    state, _ = analyzer.analyze("I have a big problem with my server")
    assert state == EmotionalState.CONCERNED, "Failed to detect concern"
    
    # Test Celebratory
    state, _ = analyzer.analyze("Thank you so much, it works perfectly!")
    assert state == EmotionalState.CELEBRATORY, "Failed to detect celebration"
    
    # Test Frustrated
    state, _ = analyzer.analyze("This is stupid, it keeps crashing!!")
    assert state == EmotionalState.FRUSTRATED, "Failed to detect frustration"
    
    print("[PASS] Emotional Analyzer")

def test_rag_engine():
    print("[TEST] RAG Engine...")
    db_path = "test_temp.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    rag = RAGEngine(db_path)
    rag.insert("What is Neuro-Lite?", "A lightweight empathic engine.", "test")
    
    results = rag.search("Neuro-Lite")
    assert len(results) > 0, "Search failed to find result"
    assert "empathic" in results[0]['answer'], "Result content mismatch"
    
    os.remove(db_path)
    print("[PASS] RAG Engine")

def test_context_manager():
    print("[TEST] Context Manager...")
    cm = ContextManager(max_history_tokens=50) # Very small for testing
    cm.add_message("user", "Hello, this is a test message.")
    cm.add_message("assistant", "I understand.")
    
    # Force overflow
    cm.add_message("user", "A" * 200) 
    ctx = cm.get_full_context()
    
    # Check if bridging happened (history compression)
    assert len(ctx) < 5, "History compression failed"
    assert any("Context summary" in m['content'] for m in ctx), "Bridge summary missing"
    print("[PASS] Context Manager")

def test_post_processor():
    print("[TEST] Post Processor...")
    
    # Test Empathy Injection
    text = "The server is down."
    res = PostProcessor.process(text, "concerned")
    assert "I understand the issue" in res, "Empathy injection failed"
    
    # Test No Duplicate
    res2 = PostProcessor.process(res, "concerned")
    assert res2.count("I understand the issue") == 1, "Duplicated empathy"
    
    print("[PASS] Post Processor")

def test_validator():
    print("[TEST] Data Validator...")
    db_path = "test_val.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    v = DataValidator(db_path)
    
    # Test PII
    valid, reason = v.validate_text("My email is test@example.com")
    assert not valid and "PII" in reason, "PII detection failed"
    
    # Test Toxicity
    valid, reason = v.validate_text("I hate this product")
    assert not valid and "Toxic" in reason, "Toxicity detection failed"
    
    # Test Valid
    valid, reason = v.validate_text("How do I restart?")
    assert valid, "Valid text rejected"
    
    os.remove(db_path)
    print("[PASS] Data Validator")

if __name__ == "__main__":
    print("=== NEURO-LITE TEST SUITE ===")
    try:
        test_emotional_analyzer()
        test_rag_engine()
        test_context_manager()
        test_post_processor()
        test_validator()
        print("\n=== ALL TESTS PASSED ===")
    except AssertionError as e:
        print(f"\n[FAIL] Test Assertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
