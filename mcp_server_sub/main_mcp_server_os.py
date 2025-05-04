import os
import platform
import random
import socket
import string
import subprocess
import re
from datetime import datetime
import psutil
from tools_registry import tool

@tool(
    name="get_desktop_path",
    description="📁 取得目前使用者的桌面路徑",
    returns="字串，桌面完整路徑",
    parameters={}
)
def get_desktop_path():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Desktop")
    else:
        return os.path.join(os.environ["HOME"], "Desktop")

@tool(
    name="get_current_time",
    description="🕒 取得目前時間（格式：YYYY-MM-DD_HHMMSS）",
    returns="時間字串",
    parameters={}
)
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")

@tool(
    name="check_internet_connection",
    description="🌐 檢查是否有網路連線",
    returns="網路連線狀態",
    parameters={}
)
def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "✅ 網際網路連線可用。"
    except OSError:
        return "❌ 無法連線至網際網路。"
    except Exception as e:
        return f"❌ 檢查網路連線時發生錯誤: {str(e)}"

@tool(
    name="get_system_info",
    description="💻 取得系統資訊（作業系統、CPU、記憶體、硬碟使用量）",
    returns="系統資訊摘要",
    parameters={}
)
def get_system_info():
    try:
        os_name = platform.system()
        os_version = platform.version()
        result = f"作業系統: {os_name} {os_version}\n"

        if psutil:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            result += (
                f"CPU: {cpu_count} 核心, 使用率 {cpu_usage}%\n"
                f"記憶體: 已使用 {memory.used / 2**30:.2f} GB / 共 {memory.total / 2**30:.2f} GB ({memory.percent}%)\n"
                f"硬碟: 已使用 {disk.used / 2**30:.2f} GB / 共 {disk.total / 2**30:.2f} GB ({disk.percent}%)"
            )
        else:
            result += "(psutil 模組未安裝，無法取得詳細系統資訊)"
        return result
    except Exception as e:
        return f"❌ 取得系統資訊失敗: {str(e)}"

@tool(
    name="get_ip_address",
    description="🔢 取得本機 IP 位址",
    returns="IP 位址資訊",
    parameters={}
)
def get_ip_address():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return f"主機名稱: {hostname}\n本機 IP: {local_ip}"
    except Exception as e:
        return f"❌ 取得 IP 位址資訊失敗: {str(e)}"

@tool(
    name="generate_random_string",
    description="🎲 產生指定長度的隨機字串",
    parameters={
        "length": "字串長度",
        "include_digits": "是否包含數字（true/false）",
        "include_special_chars": "是否包含特殊字元（true/false）"
    },
    returns="產生的隨機字串"
)
def generate_random_string(length, include_digits="true", include_special_chars="false"):
    try:
        length = int(length)
        if length <= 0:
            return "❌ 長度必須是正數"

        letters = string.ascii_letters
        digits = string.digits if include_digits.lower() == "true" else ""
        special = string.punctuation if include_special_chars.lower() == "true" else ""
        pool = letters + digits + special

        if not pool:
            return "❌ 未選擇任何字元集"

        return ''.join(random.choice(pool) for _ in range(length))
    except Exception as e:
        return f"❌ 產生隨機字串失敗: {str(e)}"

@tool(
    name="calculate_expression",
    description="🧮 計算數學表達式",
    parameters={"expression": "數學表達式"},
    returns="計算結果"
)
def calculate_expression(expression):
    try:
        sanitized = re.sub(r'[^\d\+\-\*\/\(\)\.\s]', '', expression)
        if sanitized != expression:
            return "❌ 表達式包含無效字元"
        return str(eval(sanitized))
    except Exception as e:
        return f"❌ 計算失敗: {str(e)}"

@tool(
    name="get_hostname",
    description="🔠 取得主機名稱",
    returns="主機名稱",
    parameters={}
)
def get_hostname():
    try:
        return socket.gethostname()
    except Exception as e:
        return f"❌ 取得主機名稱失敗: {str(e)}"

@tool(
    name="get_env_var",
    description="🌿 取得環境變數",
    parameters={"name": "環境變數名稱"},
    returns="變數值或錯誤訊息"
)
def get_env_var(name):
    return os.environ.get(name, f"❌ 找不到變數: {name}")

'''
@tool(
    name="reboot_system",
    description="🔁 重新啟動系統（⚠️ 需小心使用）",
    returns="✅ 已嘗試重新啟動系統"
)
def reboot_system():
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/r", "/t", "0"])
        else:
            subprocess.Popen(["reboot"])
        return "✅ 正在重新啟動系統..."
    except Exception as e:
        return f"❌ 重新啟動失敗: {str(e)}"
'''
        
'''
@tool(
    name="shutdown_system",
    description="⛔ 關閉系統（⚠️ 需小心使用）",
    returns="✅ 已嘗試關閉系統"
)
def shutdown_system():
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "0"])
        else:
            subprocess.Popen(["shutdown", "-h", "now"])
        return "✅ 正在關閉系統..."
    except Exception as e:
        return f"❌ 關閉系統失敗: {str(e)}"
'''