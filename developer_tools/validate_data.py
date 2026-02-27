#!/usr/bin/env python3
import re
import sqlite3
import hashlib
import logging

logging.basicConfig(level=logging.INFO)

class DataValidator:
    """
    Zero Trust Ingestion Validator.
    Checks: PII, Toxicity, Duplicates.
    """
    
    # Regex for basic PII (Email, Phone, IP)
    PII_PATTERNS = [
        re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b'), # Email
        re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b'), # Phone
        re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b') # IPv4
    ]

    # Basic Toxic Keyword List (Production would use a larger set)
    TOXIC_KEYWORDS = [
        "hate", "kill", "attack", "illegal", "fraud", "scam"
    ]

    def __init__(self, db_path):
        self.db_path = db_path
        self.hash_set = set()
        self._load_existing_hashes()

    def _load_existing_hashes(self):
        if not os.path.exists(self.db_path):
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT question || answer FROM knowledge")
                for row in cursor:
                    h = hashlib.md5(row[0].encode()).hexdigest()
                    self.hash_set.add(h)
        except Exception as e:
            logging.warning(f"Could not load existing hashes: {e}")

    def validate_text(self, text: str) -> tuple:
        """
        Returns (is_valid, reason)
        """
        
        # 1. PII Check
        for pattern in self.PII_PATTERNS:
            if pattern.search(text):
                return False, "PII Detected"
        
        # 2. Toxicity Check
        lower_text = text.lower()
        for word in self.TOXIC_KEYWORDS:
            if word in lower_text:
                return False, f"Toxic content ({word}) detected"

        # 3. Duplicate Check
        h = hashlib.md5(text.encode()).hexdigest()
        if h in self.hash_set:
            return False, "Duplicate entry"
        
        return True, "Valid"

    def scan_file(self, filepath: str):
        """
        Scans a text file of Q&A pairs (format: Q: ... A: ...)
        """
        import os
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return

        with open(filepath, 'r') as f:
            content = f.read()
        
        # Simple parser for example
        blocks = content.split("\n\n")
        valid_count = 0
        
        for block in blocks:
            is_valid, reason = self.validate_text(block)
            if is_valid:
                self.hash_set.add(hashlib.md5(block.encode()).hexdigest())
                valid_count += 1
                # Ingest logic would go here
            else:
                logging.warning(f"REJECTED: {reason} - Content: {block[:20]}...")
        
        logging.info(f"Scan complete. Valid: {valid_count}, Rejected: {len(blocks) - valid_count}")

if __name__ == "__main__":
    import os
    v = DataValidator("data/knowledge.db")
    # Create a dummy file for testing
    with open("temp_data.txt", "w") as f:
        f.write("Q: What is your email? A: It is test@test.com.\n\nQ: How to code? A: Use python.")
    
    v.scan_file("temp_data.txt")
    os.remove("temp_data.txt")
