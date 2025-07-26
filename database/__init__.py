"""
Database module - PostgreSQL + PGVector for web testing automation
"""

import os
import time
import hashlib
import psycopg
import uuid
from typing import Optional, List, Dict, Any
from langchain_openai import OpenAIEmbeddings

# CONN_STR will be initialized in init_database() to ensure environment variables are loaded
CONN_STR = None

_EMBEDDER = None

def get_embeddings():
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512)
    return _EMBEDDER

def _to_vector_literal(vec: list[float]) -> str:
    return '[' + ','.join(f'{v:.6f}' for v in vec) + ']'

def init_database():
    global CONN_STR
    if CONN_STR is None:
        CONN_STR = os.getenv("DATABASE_URL", "postgresql://maolin@localhost:5432/web_testing")
    
    with psycopg.connect(CONN_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            _create_tables(cur)
            _create_indexes(cur)
            conn.commit()


def _create_tables(cursor):
    """Create database tables"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            start_ts TIMESTAMP DEFAULT NOW(),
            status TEXT DEFAULT 'running',
            user_id TEXT,
            model TEXT DEFAULT 'gpt-4o',
            duration INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            type TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding VECTOR(512),
            summary TEXT,
            timestamp TIMESTAMP DEFAULT NOW(),
            url TEXT,

            CONSTRAINT fk_artifacts_run_id
                FOREIGN KEY (run_id) REFERENCES runs(run_id)
                ON DELETE CASCADE
        );
    """)


def _create_indexes(cursor):
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_runs_start_ts ON runs(start_ts);",
        "CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON artifacts(run_id);",
        "CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type);"
    ]
    for sql in indexes:
        cursor.execute(sql)
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_embedding ON artifacts USING hnsw (embedding vector_cosine_ops);")
    except:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_embedding ON artifacts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")

def _generate_artifact_summary(user_request: str, tool_name: str, text: str) -> str:
    """Generate summary for artifact storage"""
    try:
        from agent.utils import generate_smart_summary, format_summary_for_storage
        summary_dict = generate_smart_summary(user_request, tool_name, text[:500])
        return format_summary_for_storage(summary_dict)
    except Exception as e:
        print(f"❌ Failed to generate artifact summary: {repr(e)}")
        return ""


def save_artifact(run_id: str, art_type: str, text: str, url: str = "", user_request: str = "", tool_name: str = "") -> tuple:
    try:
        summary = ""
        if user_request and tool_name:
            summary = _generate_artifact_summary(user_request, tool_name, text)

        embedding_vector = get_embeddings().embed_query(text)
        artifact_id = save_artifact_to_db(run_id, art_type, text, embedding_vector, summary, url)
        return bool(artifact_id), summary
    except Exception as e:
        print(f"❌ Failed to save artifact: {repr(e)}")
        return False, ""

def search_artifacts_advanced(query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[dict]:
    try:
        query_vector = get_embeddings().embed_query(query)
        
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, run_id, type, text, summary, timestamp, url,
                           embedding <=> %s::vector as distance
                    FROM artifacts
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_vector, query_vector, k))

                results = []
                for row in cur.fetchall():
                    results.append({
                        "content": row[3],
                        "metadata": {
                            "doc_id": row[0], "run_id": row[1], "type": row[2],
                            "summary": row[4], "timestamp": row[5], "url": row[6],
                            "distance": float(row[7])
                        },
                        "summary": row[4] or row[3][:200],
                        "doc_id": row[0],
                        "timestamp": str(row[5]) if row[5] else ""
                    })
                return results
    except Exception as e:
        print(f"❌ Search failed: {repr(e)}")
        return []

def get_content_by_id(doc_id: str) -> Optional[str]:
    try:
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT text FROM artifacts WHERE id = %s", (doc_id,))
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        print(f"❌ get_content_by_id error: {repr(e)}")
        return None

def create_run(url: str, description: str = "", user_id: str = None, model: str = "gpt-4o") -> str:
    run_id = f"run_{uuid.uuid4().hex}"
    try:
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO runs (run_id, url, description, user_id, model, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (run_id, url, description, user_id, model, 'running'))
                conn.commit()
        return run_id
    except Exception as e:
        print(f"❌ create_run error: {repr(e)}")
        return run_id

def update_run_status(run_id: str, status: str, duration: int = None) -> bool:
    try:
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                if duration:
                    cur.execute("UPDATE runs SET status = %s, duration = %s WHERE run_id = %s", (status, duration, run_id))
                else:
                    cur.execute("UPDATE runs SET status = %s WHERE run_id = %s", (status, run_id))
                conn.commit()
        return True
    except Exception as e:
        print(f"❌ update_run_status error: {repr(e)}")
        return False

def save_artifact_to_db(run_id: str, art_type: str, text: str, embedding: List[float], summary: str = "", url: str = "") -> str:
    content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    artifact_id = f"{run_id}_{art_type}_{content_hash}"
    try:
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO artifacts (id, run_id, type, text, embedding, summary, url)
                    VALUES (%s, %s, %s, %s, %s::vector, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                      SET text = EXCLUDED.text,
                          embedding = EXCLUDED.embedding,
                          summary = EXCLUDED.summary,
                          url = EXCLUDED.url
                    """,
                    (artifact_id, run_id, art_type, text, _to_vector_literal(embedding), summary, url)
                )
                conn.commit()
        return artifact_id
    except Exception as e:
        print(f"❌ save_artifact_to_db error: {repr(e)}")
        return ""

class DatabaseCompat:
    async def connect(self):
        init_database()
        
    async def close(self):
        pass
        
    async def create_run(self, url: str, description: str = "", user_id: str = None, model: str = "gpt-4o") -> str:
        return create_run(url, description, user_id, model)
        
    async def update_run_status(self, run_id: str, status: str, duration: int = None) -> bool:
        return update_run_status(run_id, status, duration)
        
    async def save_artifact(self, run_id: str, artifact_type: str, content: str, url: str = "", user_request: str = "", tool_name: str = "") -> tuple:
        return save_artifact(run_id, artifact_type, content, url, user_request, tool_name)
        
    async def get_recent_runs(self, limit: int = 10):
        try:
            with psycopg.connect(CONN_STR) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT run_id, url, start_ts, status, duration, description FROM runs ORDER BY start_ts DESC LIMIT %s", (limit,))
                    return [{"run_id": row[0], "url": row[1], "start_ts": row[2], "status": row[3], "duration": row[4], "description": row[5]} for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ get_recent_runs error: {repr(e)}")
            return []

db = DatabaseCompat()
