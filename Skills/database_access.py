from .registry import registry
import sqlite3
import os

@registry.register(
    name="execute_sql",
    description="Executes a raw SQL statement on a local SQLite database file.",
    parameters={
        "query": {"type": "string", "description": "The SQL query to execute."},
        "db_name": {"type": "string", "description": "Name of the local database file (default: deep claw_default.db)"}
    }
)
def execute_sql(query: str, db_name: str = "deep claw_default.db") -> str:
    try:
        os.makedirs("chroma_db/sql_data", exist_ok=True)
        db_path = os.path.join("chroma_db/sql_data", db_name)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            conn.close()
            return f"Results: {rows}"
        else:
            conn.commit()
            conn.close()
            return "Query executed and committed successfully."
    except Exception as e:
        return f"SQL Error: {str(e)}"
