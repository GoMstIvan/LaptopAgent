import requests
import json
import re
import platform
import subprocess
import time

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:12b-it-qat"
MCP_URL = "http://localhost:5005/execute"
TOOLS_URL = "http://localhost:5005/tools"

# === 工具呼叫解析 ===
tool_pattern = re.compile(r"<tool>\s*(.*?)\((.*?)\)\s*</tool>", re.DOTALL)

def parse_tool_call(response_text):
    match = tool_pattern.search(response_text)
    if not match:
        return None

    tool_name = match.group(1).strip()
    raw_args = match.group(2).strip()

    args = {}
    for arg in re.findall(r"(\w+)\s*=\s*\"(.*?)\"", raw_args):
        args[arg[0]] = arg[1]

    return tool_name, args

def contains_tool_call(text):
    return bool(tool_pattern.search(text))

def execute_tool(action, params):
    res = requests.post(MCP_URL, json={"action": action, "params": params})
    if res.status_code != 200:
        return f"❌ Error: {res.json().get('detail')}"
    return res.json().get("result")

def get_available_tools():
    res = requests.get(TOOLS_URL)
    return res.json()

def generate_prompt(task, tools, context=[]):
    tool_descriptions = "\n".join([
        f"- {tool['name']}({', '.join(tool['parameters'].keys())})"
        for tool in tools
    ])

    prompt = f"""
You are a tool-calling assistant. You must solve the following task using ONE tool call at a time.

🛠️ Available tools:
{tool_descriptions}

📦 Tool Call Format:
<tool>tool_name(param1=\"value1\", param2=\"value2\")</tool>

🧩 Tool Call Rules:
- Only ONE tool call per response.
- You must NEVER call one tool inside another (e.g., path=get_desktop_path() ❌).
- If you need a value (like the desktop path), call a tool to get it first.
- In the NEXT response, use that result to call the next tool.
- If the task is complete, respond only with: <done>
- Do NOT explain anything. ONLY output the tool call block in this format: <tool>...</tool> or <done>.

🎯 Task:
{task}
"""

    for idx, result in enumerate(context, 1):
        prompt += f"\n# Result {idx} from previous tool:\n{result}\nBased on this result, continue solving the task."

    prompt += "\nWhat is your next tool call?"
    return prompt

def chat_with_llm(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
    )
    response.raise_for_status()
    return response.json()["response"]

# === 主程式 ===
def main():
    task = "請在桌面建立一個名為 test123 的資料夾"

    if platform.system() != "Windows":
        try:
            subprocess.check_output(["pgrep", "ollama"])
        except subprocess.CalledProcessError:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)

    print("🔍 取得工具清單...")
    tools = get_available_tools()

    context = []
    retry_count = 0

    while True:
        prompt = generate_prompt(task, tools, context)
        reply = chat_with_llm(prompt).strip()

        print("\n🧠 LLM 回應:\n", reply)

        if reply == "<done>":
            print("🎯 模型認定任務已完成。")
            break

        if not reply.startswith("<tool>") or not reply.endswith("</tool>"):
            print("⚠️ 格式錯誤：請使用 <tool>...</tool> 格式。正在重試...")
            retry_count += 1
            if retry_count > 5:
                print("❌ 重試次數過多，任務中止。")
                break
            continue

        if contains_tool_call(reply):
            tool_name, params = parse_tool_call(reply)
            print(f"\n🔧 呼叫工具: {tool_name}({params})")
            result = execute_tool(tool_name, params)
            context.append(f"Tool: {tool_name}({params})\nResult: {result}")
            print(f"✅ 工具結果: {result}\n")
            retry_count += 1
            if retry_count > 10:
                print("⚠️ 工具呼叫過多次，停止。")
                break
        else:
            print("⚠️ 未偵測到 <tool> 呼叫，可能模型偏離任務，正在重試...")
            retry_count += 1
            if retry_count > 5:
                print("❌ 重試次數過多，任務中止。")
                break
            continue

if __name__ == "__main__":
    main()
