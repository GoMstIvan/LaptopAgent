import re
import requests
from tools_registry import tool

@tool(
    name="translate_text",
    description="🌐 使用 LibreTranslate 翻譯文字",
    parameters={"text": "原始文字", "target_language": "目標語言（如 'en', 'zh', 'ja'）", "source_language": "來源語言（可選，預設為 auto）"},
    returns="翻譯後文字"
)
def translate_text(text, target_language, source_language="auto"):
    try:
        res = requests.post("https://libretranslate.de/translate", data={
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text"
        }, timeout=10)
        res.raise_for_status()
        return res.json().get("translatedText", "[翻譯失敗]")
    except Exception as e:
        return f"❌ 翻譯失敗: {str(e)}"

@tool(
    name="calculate_expression",
    description="🧮 計算數學表達式",
    parameters={"expression": "數學表達式"},
    returns="計算結果"
)
def calculate_expression(expression):
    try:
        sanitized = re.sub(r'[^\d\+\-\*/().\s]', '', expression)
        if sanitized != expression:
            return "❌ 表達式包含無效字元"
        result = eval(sanitized)
        return f"表達式: {expression}\n結果: {result}"
    except Exception as e:
        return f"❌ 計算失敗: {str(e)}"

@tool(
    name="text_to_uppercase",
    description="🔠 將文字轉換為大寫",
    parameters={"text": "要轉換的文字"},
    returns="大寫文字"
)
def text_to_uppercase(text):
    try:
        return text.upper()
    except Exception as e:
        return f"❌ 轉換失敗: {str(e)}"

@tool(
    name="text_to_lowercase",
    description="🔡 將文字轉換為小寫",
    parameters={"text": "要轉換的文字"},
    returns="小寫文字"
)
def text_to_lowercase(text):
    try:
        return text.lower()
    except Exception as e:
        return f"❌ 轉換失敗: {str(e)}"

@tool(
    name="count_words",
    description="🧮 統計文字中的字元與單字數量",
    parameters={"text": "要分析的文字"},
    returns="字數與單字數"
)
def count_words(text):
    try:
        words = re.findall(r'\w+', text)
        return f"字元數: {len(text)}, 單字數: {len(words)}"
    except Exception as e:
        return f"❌ 統計失敗: {str(e)}"

@tool(
    name="detect_language",
    description="🌍 偵測輸入文字的語言",
    parameters={"text": "要分析的文字"},
    returns="語言代碼"
)
def detect_language(text):
    try:
        res = requests.post("https://libretranslate.de/detect", data={"q": text}, timeout=10)
        res.raise_for_status()
        lang = res.json()[0].get("language", "")
        return f"偵測語言: {lang}"
    except Exception as e:
        return f"❌ 偵測失敗: {str(e)}"

@tool(
    name="clean_text",
    description="🧹 清洗文字，移除標點與多餘空白",
    parameters={"text": "要清洗的文字"},
    returns="清洗後文字"
)
def clean_text(text):
    try:
        cleaned = re.sub(r'[\W_]+', ' ', text)
        return ' '.join(cleaned.split())
    except Exception as e:
        return f"❌ 清洗失敗: {str(e)}"

@tool(
    name="to_fullwidth",
    description="🔤 將文字轉換為全形",
    parameters={"text": "要轉換的文字"},
    returns="全形文字"
)
def to_fullwidth(text):
    try:
        return ''.join(chr(ord(c) + 0xFEE0) if 33 <= ord(c) <= 126 else c for c in text)
    except Exception as e:
        return f"❌ 全形轉換失敗: {str(e)}"

@tool(
    name="to_halfwidth",
    description="🔡 將文字轉換為半形",
    parameters={"text": "要轉換的文字"},
    returns="半形文字"
)
def to_halfwidth(text):
    try:
        return ''.join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in text)
    except Exception as e:
        return f"❌ 半形轉換失敗: {str(e)}"
