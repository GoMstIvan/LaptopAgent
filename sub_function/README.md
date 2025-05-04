1. 開始
2. 是否ollama serve執行中, 如果沒有則啟動ollama serve
3. 開始對話, 預設模型gemma3:12b-it-qat, 產生一個對話ID, 使用stream回覆、對話紀錄儲存下來, 使用XML格式
  - `<User>...</User>` for user messages
  - `<System>...</System>` for system messages
  - `<Assistant>...</Assistant>` for assistant responses
4. 收到 /exit、/quit、/bye, 結束當下對話, 並且執行/save, 將對話紀錄用{ID}.md當作檔名存到conversations下
5. 收到 /save, 將conversation以{ID}.md存到conversations底下
6. 收到 /load + {ID}, 將conversations/{ID}.md 內容加入至目前對話中
7. 收到 /new, 代表開啟一個新對話, 原本舊對話用 /save 動作


8. 收到 /image + {relative_path}, 將模型切換成llama3.2-vision, 對該圖片產生描述
9. 收到 /tool, 先跟mcp_server確定有哪些工具可以用、每個工具的參數為何, 然後呼叫tool, 得到的答案插入conversation, 最後總解, ex: /tool 請幫我在桌面建立abc資料夾, assistant應該要先取得桌面路徑, 然後create_folder

Prompt: 有這些工具可以使用, 我也附上了每個工具需要的參數。請你規劃一個行程, 呼叫工具, 要呼叫的工具放在<tool>...</tool>中, 並將呼叫的結果放在<result>...</result>中。重新產生Prompt, 直到所有工具呼叫都結束, 確保conversation中只有<result>沒有<tool>
拆分子任務, 子任務結果紀錄於共享記憶, 直到所有子任務完成


10. <think></think>的功能
11. RAG、GraphRAG的功能
12. 產生圖片的功能
13. 語音的功能TTS, STT


14. txt2img、img2img:
-> 將模型放到:stable-diffusion-webui\models\Stable-diffusion, 可以從civita or huggingface下載.safetensor or checkpoint
-> python launch.py --api

15.
* 1.網頁交互模組(操作型、API型)、
* 2.桌面自動化模組(pyautogui)、
* 3.終端指令模組
