import re
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = str(Path(__file__).resolve().parents[1] / "data" / "banco.db")


def _resolve_db_path(db_path: str | None = None) -> str:
    return db_path or DEFAULT_DB_PATH


def _quote_identifier(identifier: str) -> str:
    return f'[{identifier.replace("]", "]]" )}]'


def get_schema(db_path: str | None = None) -> dict[str, list[str]]:
    resolved_db_path = _resolve_db_path(db_path)
    conn = sqlite3.connect(resolved_db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    )
    tables = [table_name for (table_name,) in cursor.fetchall()]

    schema: dict[str, list[str]] = {}
    for table_name in tables:
        cursor.execute(f"PRAGMA table_info({_quote_identifier(table_name)});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]

    conn.close()
    return schema


def get_table_info(table_name: str, db_path: str | None = None) -> dict[str, object]:
    resolved_db_path = _resolve_db_path(db_path)
    conn = sqlite3.connect(resolved_db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    create_row = cursor.fetchone()
    if not create_row:
        conn.close()
        raise ValueError(f"Tabela '{table_name}' não encontrada.")

    cursor.execute(f"PRAGMA table_info({_quote_identifier(table_name)});")
    columns = cursor.fetchall()
    conn.close()

    return {
        "table": table_name,
        "create_sql": create_row[0],
        "columns": [
            {
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default": col[4],
                "pk": bool(col[5]),
            }
            for col in columns
        ],
    }


def schema_as_text(db_path: str | None = None) -> str:
    schema = get_schema(db_path)
    lines: list[str] = []
    for table_name, columns in schema.items():
        lines.append(f"{table_name}: {', '.join(columns)}")
    return "\n".join(lines)


def get_sample_rows(table_name: str, limit: int = 10, db_path: str | None = None) -> list[tuple]:
    resolved_db_path = _resolve_db_path(db_path)
    conn = sqlite3.connect(resolved_db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def _ensure_limit(query: str, max_rows: int) -> str:
    normalized_query = query.strip().rstrip(";")
    if re.search(r"\bLIMIT\b", normalized_query, re.IGNORECASE):
        return f"{normalized_query};"
    return f"{normalized_query} LIMIT {max_rows};"


def execute_query(query: str, db_path: str | None = None, max_rows: int = 100) -> list[tuple]:
    resolved_db_path = _resolve_db_path(db_path)
    cleaned_query = query.strip()

    if not re.match(r"^(SELECT|WITH)\b", cleaned_query, re.IGNORECASE):
        raise ValueError("Apenas consultas SELECT/CTE são permitidas.")

    safe_query = _ensure_limit(cleaned_query, max_rows)

    conn = sqlite3.connect(resolved_db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(safe_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception:
        conn.close()
        raise


def extract_sql(text: str) -> str:
    """Extrai SQL de markdown/code-block ou trecho textual."""
    match = re.search(r"```(?:sql)?\s*\n?(.*?)\n?```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"((?:SELECT|WITH)\b.*?;)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return text.strip()