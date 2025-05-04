import os
import shutil
import zipfile
from tools_registry import tool

@tool(
    name="create_folder",
    description="📂 建立資料夾，可選擇附加資料夾名稱",
    parameters={"path": "基底路徑（必填）", "folder_name": "附加的資料夾名稱（可選）"},
    returns="✅ 資料夾建立成功訊息"
)
def create_folder(path, folder_name=None):
    try:
        full_path = os.path.join(path, folder_name) if folder_name else path
        os.makedirs(full_path, exist_ok=True)
        return f"✅ Folder created at: {full_path}"
    except Exception as e:
        return f"❌ 建立資料夾失敗: {str(e)}"

@tool(
    name="write_text_file",
    description="📝 寫入純文字檔案",
    parameters={"path": "完整檔案路徑（含.txt）", "content": "要寫入的文字內容"},
    returns="✅ 寫入成功訊息"
)
def write_text_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Written to {path}"
    except Exception as e:
        return f"❌ 寫入失敗: {str(e)}"

@tool(
    name="read_text_file",
    description="📖 讀取純文字檔內容",
    parameters={"path": "完整文字檔路徑"},
    returns="檔案內容"
)
def read_text_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"❌ 讀取失敗: {str(e)}"

@tool(
    name="list_files",
    description="🗂️ 列出資料夾內容",
    parameters={"path": "要列出的資料夾路徑"},
    returns="檔案與資料夾列表"
)
def list_files(path):
    try:
        return os.listdir(path)
    except Exception as e:
        return f"❌ 無法列出檔案: {str(e)}"

@tool(
    name="compress_files",
    description="🗜️ 將資料夾壓縮為 .zip",
    parameters={"source_path": "來源資料夾路徑", "output_path": "輸出 zip 路徑（含 .zip）"},
    returns="✅ 壓縮成功訊息"
)
def compress_files(source_path, output_path):
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)
        return f"✅ Zip created at: {output_path}"
    except Exception as e:
        return f"❌ 壓縮失敗: {str(e)}"

@tool(
    name="delete_folder",
    description="🗑️ 刪除指定路徑的資料夾",
    parameters={"path": "要刪除的資料夾完整路徑"},
    returns="✅ 刪除成功訊息"
)
def delete_folder(path):
    try:
        shutil.rmtree(path)
        return f"✅ 成功刪除資料夾: {path}"
    except Exception as e:
        return f"❌ 刪除失敗: {str(e)}"

@tool(
    name="rename_file",
    description="✏️ 重新命名檔案或資料夾",
    parameters={"source_path": "原始路徑", "new_name": "新名稱"},
    returns="✅ 重新命名成功訊息"
)
def rename_file(source_path, new_name):
    try:
        directory = os.path.dirname(source_path)
        new_path = os.path.join(directory, new_name)
        os.rename(source_path, new_path)
        return f"✅ Renamed to: {new_path}"
    except Exception as e:
        return f"❌ 重新命名失敗: {str(e)}"

@tool(
    name="copy_file",
    description="📋 複製檔案或資料夾到指定位置",
    parameters={"source_path": "來源路徑", "destination_path": "目標路徑"},
    returns="✅ 複製成功訊息"
)
def copy_file(source_path, destination_path):
    try:
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, destination_path)
        return f"✅ 已複製到: {destination_path}"
    except Exception as e:
        return f"❌ 複製失敗: {str(e)}"

@tool(
    name="extract_zip",
    description="📦 解壓縮 ZIP 檔案",
    parameters={"zip_path": "ZIP 檔案路徑", "extract_path": "解壓縮目的地"},
    returns="✅ 解壓縮成功訊息"
)
def extract_zip(zip_path, extract_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_path)
        return f"✅ 解壓縮至: {extract_path}"
    except Exception as e:
        return f"❌ 解壓縮失敗: {str(e)}"

@tool(
    name="get_file_size",
    description="📏 取得檔案大小（bytes）",
    parameters={"path": "檔案路徑"},
    returns="檔案大小 (bytes)"
)
def get_file_size(path):
    try:
        return os.path.getsize(path)
    except Exception as e:
        return f"❌ 取得大小失敗: {str(e)}"

@tool(
    name="get_file_extension",
    description="🔠 取得檔案副檔名",
    parameters={"path": "檔案路徑"},
    returns="副檔名（包含 .）"
)
def get_file_extension(path):
    try:
        return os.path.splitext(path)[1]
    except Exception as e:
        return f"❌ 取得副檔名失敗: {str(e)}"

@tool(
    name="move_file",
    description="🚚 移動檔案或資料夾",
    parameters={"source_path": "來源路徑", "destination_path": "目的地路徑"},
    returns="✅ 移動成功訊息"
)
def move_file(source_path, destination_path):
    try:
        shutil.move(source_path, destination_path)
        return f"✅ 已移動到: {destination_path}"
    except Exception as e:
        return f"❌ 移動失敗: {str(e)}"

@tool(
    name="is_path_exists",
    description="❓ 檢查路徑是否存在",
    parameters={"path": "檢查的路徑"},
    returns="true 或 false"
)
def is_path_exists(path):
    return os.path.exists(path)

@tool(
    name="is_directory",
    description="📁 判斷是否為資料夾",
    parameters={"path": "路徑"},
    returns="true 或 false"
)
def is_directory(path):
    return os.path.isdir(path)

@tool(
    name="is_file",
    description="📄 判斷是否為檔案",
    parameters={"path": "路徑"},
    returns="true 或 false"
)
def is_file(path):
    return os.path.isfile(path)
