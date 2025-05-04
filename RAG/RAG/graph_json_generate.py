import json
from pathlib import Path

# 定義節點與關係（基於之前的虛構 30 家公司）
nodes = [
    {"id": "Taiwan Chip Co", "type": "company", "description": "專注於高效能晶片設計，是多家AI設備商的核心供應商，與NeuralVision合作密切。"},
    {"id": "NeuralVision", "type": "company", "description": "製造人工智慧相機與感測器，晶片來自Taiwan Chip Co，產品被AutoCompute廣泛採用。"},
    {"id": "AutoCompute", "type": "company", "description": "自駕車系統開發商，整合NeuralVision感測器並與SkyRoute Navigation展開競爭。"},
    {"id": "SkyRoute Navigation", "type": "company", "description": "提供自駕車路徑演算法，與AutoCompute在市場上爭鋒相對，雙方同時依賴NeuralVision感測器。"},
    {"id": "GreenEnergyTech", "type": "company", "description": "製造太陽能與風力儲能模組，與ChargeX電池模組有密切合作關係。"},
    {"id": "ChargeX", "type": "company", "description": "生產次世代鋰電池，為GreenEnergyTech與HyperCycle的電力來源。"},
    {"id": "HyperCycle", "type": "company", "description": "電動車初創公司，使用GreenEnergyTech能源模組與ChargeX電池，與AutoCompute合作進行AI駕駛整合。"},
    {"id": "SmartLogix", "type": "company", "description": "倉儲自動化軟體公司，使用NeuralVision影像系統並與StackBot合作發展物流機器人。"},
    {"id": "StackBot", "type": "company", "description": "機器人製造商，與SmartLogix共同開發自動倉儲系統，並與RoboticMind競爭。"},
    {"id": "RoboticMind", "type": "company", "description": "提供工業與家庭用機器人，與StackBot競爭並試圖與AutoCompute合作拓展AI應用。"},
    {"id": "PhotonIC", "type": "company", "description": "生產光電轉換元件，是NeuralVision與SkyRoute的重要零組件供應商。"},
    {"id": "MetaMatter", "type": "company", "description": "開發AR眼鏡晶片，使用Taiwan Chip Co設計並與NeuralVision合作擴增實境技術。"},
    {"id": "DeepMedix", "type": "company", "description": "AI醫療診斷公司，影像模組由NeuralVision提供，與AutoCompute共享部分AI模型。"},
    {"id": "SecureNet", "type": "company", "description": "資安解決方案公司，保護StackBot與SmartLogix之間的通訊協議。"},
    {"id": "ByteEngine", "type": "company", "description": "高速邊緣運算平台，提供HyperCycle與AutoCompute資料處理能力。"},
    {"id": "GlassTek", "type": "company", "description": "生產高強度複合材料，是MetaMatter與HyperCycle的重要供應商。"},
    {"id": "NanoChem", "type": "company", "description": "供應先進電池化學材料，與ChargeX為長期合作夥伴。"},
    {"id": "SkyBlox", "type": "company", "description": "衛星影像處理公司，與AutoCompute與SkyRoute交換地理空間資訊。"},
    {"id": "AeroCraft", "type": "company", "description": "無人機製造商，與SkyBlox合作並使用PhotonIC元件與ChargeX電池。"},
    {"id": "ThermaSense", "type": "company", "description": "感測器模組製造商，產品整合於NeuralVision與SmartLogix機器人中。"},
    {"id": "DeepForge", "type": "company", "description": "金屬3D列印公司，為GlassTek與StackBot生產複雜結構件。"},
    {"id": "LogiLink", "type": "company", "description": "物流追蹤平台，整合SmartLogix與StackBot產品，並與SecureNet密切合作。"},
    {"id": "BioTrace", "type": "company", "description": "生物感測技術公司，供應DeepMedix與HyperCycle健康監控模組。"},
    {"id": "QuantumOptix", "type": "company", "description": "光子運算公司，與Taiwan Chip Co共同研發量子晶片。"},
    {"id": "NextGen Audio", "type": "company", "description": "開發AI語音辨識與音訊處理技術，與MetaMatter與RoboticMind整合語音模組。"},
    {"id": "TactileCore", "type": "company", "description": "製造觸覺回饋設備，供應MetaMatter與StackBot觸控介面模組。"},
    {"id": "PlasmaWare", "type": "company", "description": "製造高頻電源模組，與NanoChem合作生產穩定能量來源。"},
    {"id": "IntraCell", "type": "company", "description": "新創電池回收公司，與ChargeX及GreenEnergyTech合作建構永續回收機制。"},
    {"id": "MindSync", "type": "company", "description": "開發人機介面平台，與MetaMatter與DeepMedix合作打造神經感測系統。"},
    {"id": "EchoStream", "type": "company", "description": "即時音訊串流平台，與NextGen Audio與SmartLogix共同打造語音監控系統。"}
]

# 簡化邏輯：根據描述建立關聯邊
edges = []
for node in nodes:
    src = node["id"]
    desc = node["description"]
    for target_node in nodes:
        tgt = target_node["id"]
        if tgt != src and tgt in desc:
            relation = "related"
            if "合作" in desc:
                relation = "collaborates_with"
            elif "供應" in desc or "使用" in desc or "模組來自" in desc:
                relation = "supplies"
            elif "競爭" in desc or "爭鋒" in desc:
                relation = "competes_with"
            edges.append({"source": src, "target": tgt, "relation": relation})

graph = {
    "nodes": nodes,
    "edges": edges
}

# 儲存成 graph.json
output_path = Path("rag/graph.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)

output_path
