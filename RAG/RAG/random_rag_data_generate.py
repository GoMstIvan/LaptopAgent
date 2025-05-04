import os

# 設定資料夾名稱
folder_name = "rag"
os.makedirs(folder_name, exist_ok=True)

# 建立 30 家廠商資料（名稱 + 描述），彼此具有上下游、合作或競爭關係
companies = [
    ("ZenithSilicon", "專注於高效能晶片設計，是多家AI設備商的核心供應商，與OptiSense合作密切。"),
    ("OptiSense", "製造人工智慧相機與感測器，晶片來自ZenithSilicon，產品被DriveMind廣泛採用。"),
    ("DriveMind", "自駕車系統開發商，整合OptiSense感測器並與Navimetrix展開競爭。"),
    ("Navimetrix", "提供自駕車路徑演算法，與DriveMind在市場上爭鋒相對，雙方同時依賴OptiSense感測器。"),
    ("SolaraDynamics", "製造太陽能與風力儲能模組，與VoltForge電池模組有密切合作關係。"),
    ("VoltForge", "生產次世代鋰電池，為SolaraDynamics與ElektraMotion的電力來源。"),
    ("ElektraMotion", "電動車初創公司，使用SolaraDynamics能源模組與VoltForge電池，與DriveMind合作進行AI駕駛整合。"),
    ("AutoStacks", "倉儲自動化軟體公司，使用OptiSense影像系統並與BotCore合作發展物流機器人。"),
    ("BotCore", "機器人製造商，與AutoStacks共同開發自動倉儲系統，並與NeuronBots競爭。"),
    ("NeuronBots", "提供工業與家庭用機器人，與BotCore競爭並試圖與DriveMind合作拓展AI應用。"),
    ("Lumeonix", "生產光電轉換元件，是OptiSense與Navimetrix的重要零組件供應商。"),
    ("AugMentra", "開發AR眼鏡晶片，使用ZenithSilicon設計並與OptiSense合作擴增實境技術。"),
    ("MedicAI", "AI醫療診斷公司，影像模組由OptiSense提供，與DriveMind共享部分AI模型。"),
    ("CyberSentinel", "資安解決方案公司，保護BotCore與AutoStacks之間的通訊協議。"),
    ("DataPulse", "高速邊緣運算平台，提供ElektraMotion與DriveMind資料處理能力。"),
    ("CeramiTek", "生產高強度複合材料，是AugMentra與ElektraMotion的重要供應商。"),
    ("FusionMateria", "供應先進電池化學材料，與VoltForge為長期合作夥伴。"),
    ("Orbiview", "衛星影像處理公司，與DriveMind與Navimetrix交換地理空間資訊。"),
    ("SkySynth", "無人機製造商，與Orbiview合作並使用Lumeonix元件與VoltForge電池。"),
    ("ThermIQ", "感測器模組製造商，產品整合於OptiSense與AutoStacks機器人中。"),
    ("ForgeMetrix", "金屬3D列印公司，為CeramiTek與BotCore生產複雜結構件。"),
    ("TraceLogica", "物流追蹤平台，整合AutoStacks與BotCore產品，並與CyberSentinel密切合作。"),
    ("BioIntuit", "生物感測技術公司，供應MedicAI與ElektraMotion健康監控模組。"),
    ("PhotonCraze", "光子運算公司，與ZenithSilicon共同研發量子晶片。"),
    ("EchoNova", "開發AI語音辨識與音訊處理技術，與AugMentra與NeuronBots整合語音模組。"),
    ("Haptiva", "製造觸覺回饋設備，供應AugMentra與BotCore觸控介面模組。"),
    ("PlasmoTek", "製造高頻電源模組，與FusionMateria合作生產穩定能量來源。"),
    ("CelluCycle", "新創電池回收公司，與VoltForge及SolaraDynamics合作建構永續回收機制。"),
    ("NeuroWeave", "開發人機介面平台，與AugMentra與MedicAI合作打造神經感測系統。"),
    ("AudiaLink", "即時音訊串流平台，與EchoNova與AutoStacks共同打造語音監控系統。"),
]

# 將每個公司儲存為 .md 檔案
for name, desc in companies:
    safe_name = name.replace(" ", "_").replace("/", "_")
    filepath = os.path.join(folder_name, f"{safe_name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\n{desc}\n")

import os
os.listdir(folder_name)  # 顯示建立的檔案以供確認
