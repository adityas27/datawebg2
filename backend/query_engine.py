"""
Text-to-SQL query engine.
User question → Gemini LLM generates SQL → Execute on SQLite → Return result.
"""

import os
import sqlite3
import pandas as pd
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data.csv")
TABLE_NAME = "data_table"

# ── CSV → SQLite loader ───────────────────────────────────────────────────────

def load_csv_to_sqlite(
    csv_path: str = CSV_PATH,
    db_path: str = DB_PATH,
    table_name: str = TABLE_NAME,
) -> None:
    """Read a CSV file and write it into the SQLite database."""
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()


# ── Schema extraction ─────────────────────────────────────────────────────────

def get_table_schema(
    db_path: str = DB_PATH,
    table_name: str = TABLE_NAME,
) -> str:
    """Return a human-readable schema string for the given table."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor.fetchall()
    finally:
        conn.close()

    if not columns:
        raise ValueError(f"Table '{table_name}' not found or has no columns.")

    lines = [f"Table: {table_name}", "Columns:"]
    for col in columns:
        # PRAGMA table_info returns: (cid, name, type, notnull, default, pk)
        name, col_type = col[1], col[2]
        lines.append(f"  - {name} ({col_type})")
    return "\n".join(lines)


# ── LLM helpers ───────────────────────────────────────────────────────────────

def _build_prompt(schema: str, question: str) -> str:
    return (
        "You are a SQL expert. Given the following SQLite table schema, "
        "write a SQL query that answers the user's question.\n\n"
        "RULES:\n"
        "- Return ONLY a valid SQLite SQL query.\n"
        "- Do NOT include any explanation, markdown, or code fences.\n"
        f"- Use ONLY the table and columns listed below.\n\n"
        f"SCHEMA:\n{schema}\n\n"
        f"QUESTION: {question}\n\n"
        "SQL:"
    )


def _call_llm(prompt: str) -> str:
    """Call Gemini and return the raw text response."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()


def _clean_sql(raw: str) -> str:
    """Strip markdown fences or extra whitespace the LLM might add."""
    sql = raw.strip()
    if sql.startswith("```"):
        # Remove opening ```sql or ``` and closing ```
        lines = sql.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()
    return sql


# ── Main entry point ──────────────────────────────────────────────────────────

def ask_question(question: str) -> dict:
    """
    End-to-end pipeline:
    1. Get table schema
    2. Ask LLM to generate SQL
    3. Execute SQL
    4. Return structured result
    """
    # Ensure data is loaded
    if not _table_exists():
        if os.path.exists(CSV_PATH):
            load_csv_to_sqlite()
        else:
            return {
                "answer": "No dataset loaded. Please place a CSV file at backend/data.csv.",
                "sql_query": "",
                "result": None,
                "error": "Dataset not found.",
            }

    # 1. Schema
    try:
        schema = get_table_schema()
    except ValueError as e:
        return {"answer": str(e), "sql_query": "", "result": None, "error": str(e)}

    # 2. Generate SQL
    prompt = _build_prompt(schema, question)
    try:
        raw_sql = _call_llm(prompt)
    except Exception as e:
        return {
            "answer": "Failed to generate SQL from LLM.",
            "sql_query": "",
            "result": None,
            "error": str(e),
        }

    sql_query = _clean_sql(raw_sql)

    # 3. Execute SQL
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(sql_query)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description] if cursor.description else []
        result = [dict(zip(col_names, row)) for row in rows]
    except Exception as e:
        return {
            "answer": "SQL execution failed.",
            "sql_query": sql_query,
            "result": None,
            "error": str(e),
        }
    finally:
        conn.close()

    # 4. Build natural-language answer
    answer = _generate_answer(question, sql_query, result)

    return {
        "answer": answer,
        "sql_query": sql_query,
        "result": result,
    }


def _table_exists(
    db_path: str = DB_PATH,
    table_name: str = TABLE_NAME,
) -> bool:
    """Check if the data table already exists in the database."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def _generate_answer(question: str, sql_query: str, result: list) -> str:
    """Ask the LLM to summarise the SQL result in natural language."""
    prompt = (
        "You are a helpful data analyst. The user asked a question, "
        "a SQL query was run, and below are the results.\n\n"
        "Provide a clear, concise natural-language answer to the user's question "
        "based on the data. Do NOT include SQL or technical details.\n\n"
        f"QUESTION: {question}\n"
        f"SQL QUERY: {sql_query}\n"
        f"RESULT: {result}\n\n"
        "ANSWER:"
    )
    try:
        return _call_llm(prompt)
    except Exception:
        # Fallback: just describe the raw result
        return f"Query returned {len(result)} row(s)."
