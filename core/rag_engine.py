import sqlite3
import logging
import os
from typing import Optional, List

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Micro-RAG using SQLite FTS5.
    Deterministic, Sub-10ms search.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()

    def _get_connection(self):
        # isolation_level=None for autocommit mode (safe for reads)
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            with self._get_connection() as conn:
                # Create standard table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT,
                        answer TEXT,
                        source TEXT
                    )
                """)
                # Create FTS5 virtual table
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                        question, 
                        answer, 
                        content='knowledge', 
                        content_rowid='id'
                    )
                """)
                # Triggers to keep FTS in sync
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
                        INSERT INTO knowledge_fts(rowid, question, answer) 
                        VALUES (new.id, new.question, new.answer);
                    END;
                """)
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
                        INSERT INTO knowledge_fts(knowledge_fts, rowid, question, answer) 
                        VALUES('delete', old.id, old.question, old.answer);
                    END;
                """)
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
                        INSERT INTO knowledge_fts(knowledge_fts, rowid, question, answer) 
                        VALUES('delete', old.id, old.question, old.answer);
                        INSERT INTO knowledge_fts(rowid, question, answer) 
                        VALUES (new.id, new.question, new.answer);
                    END;
                """)
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def search(self, query: str, limit: int = 3) -> List[dict]:
        """
        FTS5 MATCH search.
        Returns list of dicts.
        """
        results = []
        try:
            with self._get_connection() as conn:
                # Sanitize query for FTS5 (remove special chars like ' or ")
                clean_query = query.replace("'", " ").replace('"', " ")
                # Use simple token matching
                fts_query = " ".join([f'"{token}"*' for token in clean_query.split()])
                
                sql = """
                    SELECT k.question, k.answer, k.source 
                    FROM knowledge_fts f
                    JOIN knowledge k ON f.rowid = k.id
                    WHERE knowledge_fts MATCH ?
                    ORDER BY bm25(knowledge_fts) -- Built-in ranking
                    LIMIT ?
                """
                cursor = conn.execute(sql, (fts_query, limit))
                rows = cursor.fetchall()
                
                for row in rows:
                    results.append({
                        "question": row["question"],
                        "answer": row["answer"],
                        "source": row["source"]
                    })
        except sqlite3.OperationalError as e:
            # FTS5 might error on query syntax if user inputs weird chars
            logger.warning(f"FTS5 Search syntax error: {e}")
            return []
        except Exception as e:
            logger.error(f"RAG Search Error: {e}")
            
        return results

    def insert(self, question: str, answer: str, source: str = "manual"):
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO knowledge (question, answer, source) VALUES (?, ?, ?)",
                    (question, answer, source)
                )
        except Exception as e:
            logger.error(f"RAG Insert Error: {e}")
