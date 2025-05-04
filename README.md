```simple_flowchart
          [User Prompt]
                ↓
         main_tool.py
                ↓
       generate_plan() ➝ [Ollama API /api/generate]
                ↓
          LLM 回傳 JSON Steps
                ↓
          execute_steps()
              ↙        ↘
  resolve_param_value   ➝ POST to /execute (MCP Server)
                                ↓
                        Tool function mapping
                                ↓
                         回傳結果更新 context
```


| 項目        | `json_base`           | `inline_xml`       | `native`               | `code_gen`     |
| --------- | --------------------- | ------------------ | ---------------------- | -------------- |
| 🧠 模型任務   | 規劃步驟                  | 決定是否呼叫工具           | 選擇工具與填參數               | 撰寫執行邏輯         |
| 📦 資料格式   | JSON Array            | `<tool>...</tool>` | OpenAI Function schema | Python code    |
| 🧩 工具傳遞邏輯 | context 變數 `${{...}}` | 明確參數值              | JSON tool\_call        | 自行定義變數         |
| 🔁 執行流程   | 批次執行                  | 每回合逐步互動            | LLM 內建調用               | 動態執行 Python    |
| 🧰 適用範例   | 任務：建立資料夾＋寫檔           | 任務：查天氣、翻譯、查 IP     | 任務：查航班、訂票              | 任務：資料分析、計算公式   |
| 🧠 智能化程度  | 高（但不交互）               | 高（適合思考回饋）          | 中（受限 API）              | 非常高（LLM 可任意邏輯） |

Tool Call模式總覽
| 模式                             | 說明                                           | 適用場景                 | 範例                  |
| ------------------------------ | -------------------------------------------- | -------------------- | ------------------- |
| 1️⃣ One-shot JSON Planning     | 一次產出完整步驟（JSON array）                         | 固定流程任務               | 建立資料夾 → 寫入檔案        |
| 2️⃣ Iterative XML Tool Call    | 單步逐次執行（inline `<tool>...`）                   | 有依賴的多步任務             | 取得桌面路徑 → 建立資料夾      |
| 3️⃣ ReAct-style + Thought      | 交錯 `<think>thought</think>` 與 `<tool>...`    | 需要模型推理規劃流程           | 需要思考是否壓縮或翻譯         |
| 4️⃣ Self-Reflective Tool Agent | 使用 `<observe>` + `<tool>` + `<plan>`         | Meta-cognitive agent | 自我糾錯、自我調整目標         |
| 5️⃣ Streaming DSL Parser       | 模型輸出自定 DSL（如 `tool: name(param=val)`）並即時解析執行 | 適合多工具混合、模仿 Bash      | 更自由的互動式 agent shell |
