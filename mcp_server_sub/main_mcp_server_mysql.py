import pymysql
from tools_registry import tool

# === MySQL connection settings ===
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "your_db"
}

def get_connection():
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

@tool(
    name="mysql_create_table",
    description="🧱 建立 MySQL 資料表（透過 DDL 語句）",
    parameters={"ddl": "完整的 CREATE TABLE 語句"},
    returns="建立結果"
)
def mysql_create_table(ddl):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(ddl)
            conn.commit()
        return "✅ 資料表建立成功"
    except Exception as e:
        return f"❌ 建立失敗: {str(e)}"

@tool(
    name="mysql_insert_data",
    description="📥 插入資料至指定資料表",
    parameters={"table": "資料表名稱", "columns": "欄位名稱（以逗號分隔）", "values": "對應值（以逗號分隔）"},
    returns="插入結果"
)
def mysql_insert_data(table, columns, values):
    try:
        col_list = [col.strip() for col in columns.split(",")]
        val_list = [val.strip() for val in values.split(",")]
        placeholders = ", ".join(["%s"] * len(val_list))
        sql = f"INSERT INTO {table} ({', '.join(col_list)}) VALUES ({placeholders})"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, val_list)
            conn.commit()
        return "✅ 插入成功"
    except Exception as e:
        return f"❌ 插入失敗: {str(e)}"

@tool(
    name="mysql_query_data",
    description="🔍 查詢資料（SELECT 語句）",
    parameters={"query": "完整的 SELECT 語句"},
    returns="查詢結果（JSON 格式）"
)
def mysql_query_data(query):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        return results
    except Exception as e:
        return f"❌ 查詢失敗: {str(e)}"

@tool(
    name="mysql_update_data",
    description="✏️ 更新資料（UPDATE 語句）",
    parameters={"sql": "完整 UPDATE 語句"},
    returns="更新結果"
)
def mysql_update_data(sql):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        return "✅ 更新成功"
    except Exception as e:
        return f"❌ 更新失敗: {str(e)}"

@tool(
    name="mysql_delete_data",
    description="🗑️ 刪除資料（DELETE 語句）",
    parameters={"sql": "完整 DELETE 語句"},
    returns="刪除結果"
)
def mysql_delete_data(sql):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        return "✅ 刪除成功"
    except Exception as e:
        return f"❌ 刪除失敗: {str(e)}"

@tool(
    name="mysql_list_tables",
    description="📋 顯示所有資料表",
    parameters={},
    returns="目前資料庫中所有資料表名稱"
)
def mysql_list_tables():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[f"Tables_in_{MYSQL_CONFIG['database']}"] for row in cursor.fetchall()]
        return tables
    except Exception as e:
        return f"❌ 查詢失敗: {str(e)}"

@tool(
    name="mysql_execute_sql",
    description="⚙️ 執行任意 SQL 語句（高權限工具）",
    parameters={"sql": "任意 SQL 指令（請小心使用）"},
    returns="執行結果"
)
def mysql_execute_sql(sql):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                if sql.strip().lower().startswith("select"):
                    return cursor.fetchall()
            conn.commit()
        return "✅ 執行成功"
    except Exception as e:
        return f"❌ 執行錯誤: {str(e)}"
