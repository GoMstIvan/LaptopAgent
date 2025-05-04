import sqlite3
from tools_registry import tool

DB_PATH = "mcp_data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

@tool(
    name="create_table",
    description="📋 建立資料表",
    parameters={"table": "資料表名稱", "schema": "欄位定義（如 id INTEGER PRIMARY KEY, name TEXT）"},
    returns="建立結果"
)
def create_table(table, schema):
    try:
        with get_connection() as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema})")
        return f"✅ 資料表 {table} 建立成功"
    except Exception as e:
        return f"❌ 建立資料表失敗: {str(e)}"

@tool(
    name="insert_data",
    description="📥 插入資料到資料表",
    parameters={"table": "資料表名稱", "values": "要插入的值（逗號分隔）"},
    returns="插入結果"
)
def insert_data(table, values):
    try:
        values_list = [v.strip() for v in values.split(",")]
        placeholders = ",".join(["?"] * len(values_list))
        with get_connection() as conn:
            conn.execute(f"INSERT INTO {table} VALUES ({placeholders})", values_list)
        return f"✅ 成功插入資料: {values_list}"
    except Exception as e:
        return f"❌ 插入資料失敗: {str(e)}"

@tool(
    name="query_data",
    description="🔍 查詢資料表內容",
    parameters={"query": "完整 SQL SELECT 查詢語句"},
    returns="查詢結果"
)
def query_data(query):
    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()
        return f"查詢結果共 {len(rows)} 筆:\n" + "\n".join(map(str, rows))
    except Exception as e:
        return f"❌ 查詢失敗: {str(e)}"

@tool(
    name="delete_data",
    description="🗑️ 刪除資料",
    parameters={"query": "完整 SQL DELETE 指令"},
    returns="刪除結果"
)
def delete_data(query):
    try:
        with get_connection() as conn:
            count = conn.execute(query).rowcount
            conn.commit()
        return f"✅ 成功刪除 {count} 筆資料"
    except Exception as e:
        return f"❌ 刪除失敗: {str(e)}"

@tool(
    name="update_data",
    description="✏️ 更新資料表內容",
    parameters={"query": "完整 SQL UPDATE 指令"},
    returns="更新結果"
)
def update_data(query):
    try:
        with get_connection() as conn:
            count = conn.execute(query).rowcount
            conn.commit()
        return f"✅ 成功更新 {count} 筆資料"
    except Exception as e:
        return f"❌ 更新失敗: {str(e)}"

@tool(
    name="list_tables",
    description="📂 列出所有資料表名稱",
    returns="資料表列表",
    parameters={}
)
def list_tables():
    try:
        with get_connection() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return "📋 資料表: " + ", ".join(t[0] for t in tables)
    except Exception as e:
        return f"❌ 無法列出資料表: {str(e)}"
