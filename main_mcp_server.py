from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn

# 工具註冊器與內部工具清單
from tools_registry import TOOLS_REGISTRY, get_available_tools

# 匯入所有模組工具（確保註冊器生效）
import mcp_server_sub.main_mcp_server_os
import mcp_server_sub.main_mcp_server_filesystem
import mcp_server_sub.main_mcp_server_text
import mcp_server_sub.main_mcp_server_internet
import mcp_server_sub.main_mcp_server_sqlite

app = FastAPI()

class ExecuteRequest(BaseModel):
    action: str
    params: Dict[str, str] = {}

@app.get("/tools")
def list_tools():
    return get_available_tools()

@app.post("/execute")
def execute(req: ExecuteRequest):
    tool = next((t for t in TOOLS_REGISTRY if t["name"] == req.action), None)
    if not tool:
        raise HTTPException(status_code=404, detail=f"❌ 工具 '{req.action}' 未註冊")
    try:
        result = tool["function"](**req.params)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 執行錯誤: {str(e)}")

# ✅ 啟動伺服器
if __name__ == "__main__":
    uvicorn.run("main_mcp_server:app", host="0.0.0.0", port=5005, reload=True)