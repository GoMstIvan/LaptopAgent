import socket
import requests
import re
from tools_registry import tool

@tool(
    name="get_ip_address",
    description="🔢 取得本機與公共 IP 位址",
    returns="IP 位址資訊",
    parameters={}
)
def get_ip_address():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            public_ip = requests.get("https://api.ipify.org", timeout=5).text
        except:
            public_ip = "無法取得公共 IP"
        return f"主機名稱: {hostname}\n本機 IP: {local_ip}\n公共 IP: {public_ip}"
    except Exception as e:
        return f"❌ 取得 IP 位址資訊失敗: {str(e)}"

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
    name="duckduckgo_search",
    description="🔍 使用 DuckDuckGo 搜尋並回傳結果",
    parameters={"query": "搜尋關鍵字"},
    returns="搜尋結果"
)
def duckduckgo_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"❌ DuckDuckGo API 回傳狀態碼 {response.status_code}"
        data = response.json()
        results = []
        if data.get("Abstract"):
            results.append(f"摘要: {data['Abstract']}")
        if data.get("RelatedTopics"):
            for i, topic in enumerate(data["RelatedTopics"][:5], 1):
                if "Text" in topic:
                    results.append(f"{i}. {topic['Text']}")
        return "\n".join(results) if results else "⚠️ 找不到搜尋結果。"
    except Exception as e:
        return f"❌ 搜尋網頁時發生錯誤: {str(e)}"

@tool(
    name="get_weather",
    description="🌤️ 取得模擬天氣資訊",
    parameters={"location": "地點名稱或城市"},
    returns="天氣資訊"
)
def get_weather(location):
    import random
    try:
        condition = random.choice(["晴天", "多雲", "雨天", "雷暴", "下雪"])
        return f"{location} 天氣：{condition}, 氣溫 {random.randint(10, 30)}°C"
    except Exception as e:
        return f"❌ 取得天氣資訊失敗: {str(e)}"

@tool(
    name="ping_host",
    description="📡 Ping 指定主機",
    parameters={"host": "主機名稱或 IP 位址"},
    returns="通訊結果"
)
def ping_host(host):
    try:
        import subprocess
        result = subprocess.run(["ping", "-c", "3", host], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else f"❌ 無法 ping {host}"
    except Exception as e:
        return f"❌ Ping 失敗: {str(e)}"

@tool(
    name="get_public_ip",
    description="🌐 取得公共 IP 位址（無主機名稱）",
    returns="公共 IP",
    parameters={}
)
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        return f"❌ 無法取得公共 IP: {str(e)}"

@tool(
    name="resolve_hostname",
    description="🧭 DNS 查詢主機名稱對應 IP",
    parameters={"hostname": "要查詢的主機名稱"},
    returns="IP 位址"
)
def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except Exception as e:
        return f"❌ 查詢失敗: {str(e)}"

@tool(
    name="http_get",
    description="🌐 執行 HTTP GET 並回傳前幾行",
    parameters={"url": "目標網址"},
    returns="HTTP 回應預覽"
)
def http_get(url):
    try:
        response = requests.get(url, timeout=5)
        content = response.text.strip().splitlines()[:5]
        return "\n".join(content)
    except Exception as e:
        return f"❌ 取得網頁失敗: {str(e)}"

@tool(
    name="port_scan",
    description="🔎 掃描主機指定連接埠是否開啟",
    parameters={"host": "目標主機", "ports": "要掃描的連接埠列表，以逗號分隔"},
    returns="開啟的連接埠清單"
)
def port_scan(host, ports):
    try:
        ports = [int(p.strip()) for p in ports.split(",")]
        open_ports = []
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        return f"開啟的連接埠: {open_ports}" if open_ports else "未發現開啟的埠"
    except Exception as e:
        return f"❌ 埠掃描失敗: {str(e)}"