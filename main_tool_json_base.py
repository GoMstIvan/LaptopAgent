import requests
import json
import subprocess
import platform
import time
import os
import sys
import argparse
import re

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:4b"#"gemma3:12b-it-qat" #"qwen2.5:3b"
MCP_URL = "http://localhost:5005/execute"
TOOLS_URL = "http://localhost:5005/tools"

def clean_llm_json_response(response_text: str):
    """清理 LLM 回傳的 JSON 步驟陣列，使其可被 json.loads 安全解析"""

    # === Step 1: 移除 f-string 語法 ===
    response_text = response_text.replace('f"', '"').replace("f'", "'")

    # === Step 2: 修補變數語法不完整 ===
    response_text = response_text.replace('"${', '"${{').replace('}"', '}}')

    # === Step 3: 移除 markdown code block ===
    response_text = re.sub(r"```(?:json)?\s*\n(.*?)```", r"\1", response_text, flags=re.DOTALL)

    # === Step 4: 嘗試抓出 JSON array 區塊（避免多餘敘述）===
    array_match = re.search(r"\[\s*\{.*?\}\s*\]", response_text, re.DOTALL)
    if array_match:
        response_text = array_match.group(0)

    # === Step 5: 清除註解 //、多餘逗號 ===
    response_text = re.sub(r"//.*?$", "", response_text, flags=re.MULTILINE)
    response_text = re.sub(r",\s*}", "}", response_text)
    response_text = re.sub(r",\s*]", "]", response_text)

    # === Step 6: 修補變數插入語法錯誤 ===
    # ${xxx} → ${{xxx}}
    response_text = re.sub(r'\$\{([a-zA-Z0-9_]+)\}', r'${{\1}}', response_text)

    # ${{xxx}_abc → ${{xxx}}_abc
    response_text = re.sub(r'\$\{\{([a-zA-Z0-9_]+)\}_', r'${{\1}}_', response_text)

    # ${{xxx}/abc → ${{xxx}}/abc
    response_text = re.sub(r'\$\{\{([a-zA-Z0-9_]+)\}/', r'${{\1}}/', response_text)

    # ${{xxx} → ${{xxx}}
    response_text = re.sub(r'\$\{\{([a-zA-Z0-9_]+)\}(?!\})', r'${{\1}}', response_text)

    # "${{xxx}, → "${{xxx}}",
    response_text = re.sub(r'"\$\{\{([a-zA-Z0-9_]+)\},', r'"${{\1}}",', response_text)

    # 修補像 "${{xxx}, → "${{xxx}}",
    response_text = re.sub(r'"(\$\{\{[a-zA-Z0-9_]+)\},', r'"\1}}",', response_text)

    # 如果 "${{xxx}}" 沒有收尾雙引號，幫他補上（例如出現在 value 結尾）
    response_text = re.sub(r'("\$\{\{[a-zA-Z0-9_]+\}\})(?=\s*[},])', r'\1"', response_text)

    # 移除 <think> ... </think> 區段
    response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL)

    return response_text

def resolve_param_value(value: str, context: dict) -> str:
    """
    根據 context 解析變數插值
    支援格式：
    - "${var}" 或 "${{var}}"
    - 複合字串，如 "${{a}}/${{b}}/x.txt"
    """

    if not isinstance(value, str):
        return value

    # 支援複合字串插值，如 "${{a}}/subdir/${{b}}"
    def replacer(match):
        var_name = match.group(1)
        return str(context.get(var_name, f"${{{{{var_name}}}}}"))  # 若找不到保留原樣

    # 匹配 ${{var}} 或 ${var}
    return re.sub(r"\$\{\{?([a-zA-Z0-9_]+)\}?\}", replacer, value)

# === 啟動 Ollama Server（如果尚未執行）===
def is_ollama_running():
    try:
        res = requests.get(f"{OLLAMA_URL}/api/version", timeout=2)
        return res.status_code == 200
    except:
        return False

def start_ollama_server():
    print("🟡 Ollama 未啟動，正在啟動中...")
    if platform.system() == "Windows":
        subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(10):
        if is_ollama_running():
            print("✅ Ollama 已啟動")
            return True
        time.sleep(1)
    print("❌ 無法啟動 Ollama，請確認安裝與設定。")
    return False

# === 工具查詢 ===
def get_available_tools():
    res = requests.get(TOOLS_URL)
    return res.json()

# === 向 LLM 產生步驟 ===
def generate_plan(task, tools):
    tool_descriptions = "\n".join([
        f"- {tool['name']}({', '.join(tool['parameters'].keys())})"
        for tool in tools
    ])

    prompt = f"""
You are a task planner.
Your job is to break down the following task into a precise sequence of tool calls.
Each tool call may generate output, which must be used in subsequent steps.

🛠️ Available tools:
{tool_descriptions}

🧩 Output format:
- A JSON array of steps.
- Each step must be a JSON object with:
  - `"action"`: tool name
  - `"params"`: input dictionary (omit if none)
- DO NOT use Python f-strings or `${{var}}_suffix` formatting.
- DO use full variable substitution only: `"path": "${{get_desktop_path_result}}"`

⚠️ Requirements:
- If a step needs a value from another tool, you must call that tool first.
- You can only reference outputs using this format: `"${{toolname_result}}"`
- Combine strings by splitting them into separate parameters (e.g., `folder_name` and later `filename`, not combined).
- Avoid hardcoded values when a tool can provide the value.

🎯 Task:
{task}

✅ Example output:
[
  {{"action": "get_desktop_path"}},
  {{"action": "get_current_time"}},
  {{"action": "create_folder", "params": {{
    "path": "${{get_desktop_path_result}}",
    "folder_name": "${{get_current_time_result}}"
  }}}},
  {{"action": "write_text_file", "params": {{
    "path": "${{get_desktop_path_result}}/${{get_current_time_result}}/log.txt",
    "content": "這是自動建立的日誌"
  }}}}
]

🛑 DO NOT explain anything. Just return the JSON array of steps.

"""


    response = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    result = response.json()
    
    # Clean and fix the response to make it valid JSON
    response_text = result["response"]

    response_text = clean_llm_json_response(response_text)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("❌ 無法解析 LLM 回應為有效 JSON：")
        print(response_text)
        return []


# === 執行步驟 ===
def execute_steps(steps):
    context = {}
    execution_log = []

    for idx, step in enumerate(steps, 1):
        action = step["action"]
        raw_params = step.get("params", {})

        resolved_params = {}
        for k, v in raw_params.items():
            resolved_params[k] = resolve_param_value(v, context)

        print(f"\n🛠️ Step {idx}: {action}({resolved_params})")
        res = requests.post(MCP_URL, json={"action": action, "params": resolved_params})
        if res.status_code != 200:
            result = f"❌ Error: {res.json().get('detail')}"
        else:
            result = res.json().get("result")

        context[f"{action}_result"] = result
        execution_log.append({
            "step": idx,
            "action": action,
            "params": resolved_params,
            "result": result
        })

    return execution_log

# === 主程式 ===
def main():

    task = "請在桌面建立一個名為 test123 的資料夾"
    #task = "請幫我讀取桌面的 notes.txt 並幫我翻譯成英文，儲存為 translated.txt"
    #task = "請把桌面 test123 資料夾壓縮為 zip 存在 Downloads 目錄中"
    #task = "請在桌面建立一個以今天日期命名的資料夾，並建立一個 log.txt 檔案，寫入『這是自動建立的日誌』"
    #task = "請幫我讀取桌面的 notes.txt 並幫我翻譯成英文，儲存為 translated.txt"
    #task = "請把桌面 test123 資料夾壓縮為 zip 存在 Downloads 目錄中"
    #task = "請在桌面建立一個以今天日期命名的資料夾，並建立一個 log.txt 檔案，寫入『這是自動建立的日誌』"

    if not is_ollama_running():
        if not start_ollama_server():
            exit(1)

    print("🔍 取得工具清單中...")
    tools = get_available_tools()

    print("🧠 向 LLM 要求步驟計畫...")
    steps = generate_plan(task, tools)
    print(json.dumps(steps, indent=2, ensure_ascii=False))

    print("🚀 執行步驟中...")
    logs = execute_steps(steps)

    print("\n📜 完整執行結果：")
    print(json.dumps(logs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
