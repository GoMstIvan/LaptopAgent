import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/chat"

def stream_chat(model, messages):
    response = requests.post(
        OLLAMA_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": model,
            "messages": messages,
            "stream": True
        }),
        stream=True
    )

    full_reply = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                full_reply += content
            if chunk.get("done", False):
                break
    print()
    return full_reply.strip()

def run_dual_llm_debate(user_question):
    print("🧠 問題：", user_question)
    print("🔁 啟動 Assistant1 / Assistant2 對話...\n")

    # 初始角色設定
    system_prompt_1 = "You are Assistant1. Your job is to solve the user's question thoroughly and logically."
    system_prompt_2 = "You are Assistant2. Your job is to question and challenge the reasoning or assumptions made by Assistant1."

    # 對話歷史紀錄
    conversation = [
        {"role": "user", "content": user_question}
    ]

    assistant1_model = "qwen2.5:3b"
    assistant2_model = "qwen3:4b"

    # 加入 system prompt
    conversation_1 = [{"role": "system", "content": system_prompt_1}] + conversation.copy()
    conversation_2 = [{"role": "system", "content": system_prompt_2}] + conversation.copy()

    for round in range(3):
        print(f"\n🔷 Round {round+1} - Assistant1 回答")
        assistant1_reply = stream_chat(assistant1_model, conversation_1)
        conversation_1.append({"role": "assistant", "content": assistant1_reply})
        conversation_2.append({"role": "assistant", "content": assistant1_reply})

        print(f"\n🔶 Round {round+1} - Assistant2 質疑")
        assistant2_reply = stream_chat(assistant2_model, conversation_2)
        conversation_1.append({"role": "user", "content": assistant2_reply})
        conversation_2.append({"role": "user", "content": assistant2_reply})

    # 最後要求 Assistant1 給出結論
    final_question = "Please give us the final conclusion."
    print("\n🔚 Assistant2: (結尾質疑) →", final_question)
    conversation_1.append({"role": "user", "content": final_question})
    print("\n🎯 Assistant1 最終結論：")
    final_reply = stream_chat(assistant1_model, conversation_1)

    print("\n✅ 對話結束。")

if __name__ == "__main__":
    user_question = input("請輸入問題： ").strip()
    run_dual_llm_debate(user_question)
