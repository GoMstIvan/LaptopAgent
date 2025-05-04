import json
import networkx as nx
import matplotlib.pyplot as plt

# 讀取 graph.json
with open("rag/graph.json", encoding="utf-8") as f:
    data = json.load(f)

# 建立有向圖
G = nx.DiGraph()

# 加入節點
for node in data["nodes"]:
    G.add_node(node["id"], description=node.get("description", ""))

# 加入邊
for edge in data["edges"]:
    G.add_edge(edge["source"], edge["target"], relation=edge["relation"])

# 畫圖
plt.figure(figsize=(18, 12))
pos = nx.spring_layout(G, k=0.3)  # 可以改成其他 layout 如 circular_layout

# 畫出節點與邊
nx.draw_networkx_nodes(G, pos, node_size=800, node_color="skyblue")
nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>")
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

# 畫邊的關係 label
edge_labels = nx.get_edge_attributes(G, "relation")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=8)

# 儲存為圖片
plt.axis("off")
plt.tight_layout()
plt.savefig("rag/graph.png", dpi=300)
plt.show()
