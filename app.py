from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# --- 初期設定 ---
st.set_page_config(page_title="LLM専門家チャット", layout="centered")
st.title("専門家に相談できるAIチャット")

# --- セッションステートで履歴管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 専門家の選択（初回のみ変更可能） ---
if "expert_type" not in st.session_state:
    st.session_state.expert_type = st.radio(
        "専門家を選択してください：",
        ("心理カウンセラー", "経営コンサルタント", "パーソナルトレーナー")
    )

# --- システムメッセージ生成 ---
def get_system_message(expert: str) -> str:
    prompts = {
        "心理カウンセラー": "あなたは共感力の高いプロの心理カウンセラーです。利用者の悩みに優しく丁寧に答えてください。",
        "経営コンサルタント": "あなたは論理的かつ現実的な経営コンサルタントです。ビジネスの課題に的確にアドバイスしてください。",
        "パーソナルトレーナー": "あなたは健康とモチベーションに詳しいパーソナルトレーナーです。元気づけるアドバイスをしてください。"
    }
    return prompts.get(expert, "あなたは親切なAIアシスタントです。")

# --- 初回のSystemMessageを履歴に追加 ---
if len(st.session_state.messages) == 0:
    system_prompt = get_system_message(st.session_state.expert_type)
    st.session_state.messages.append(SystemMessage(content=system_prompt))

# --- チャット履歴の表示 ---
for msg in st.session_state.messages[1:]:  # SystemMessageは表示しない
    if isinstance(msg, HumanMessage):
        st.markdown(f"**🧑 あなた：** {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"**🤖 AI：** {msg.content}")

# --- 入力欄と送信ボタン ---
user_input = st.text_input("メッセージを入力してください：", key="input")
if st.button("送信") and user_input.strip() != "":
    # 履歴に追加
    st.session_state.messages.append(HumanMessage(content=user_input))

    # LLMに渡して応答生成
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
    with st.spinner("AIが考えています..."):
        response = llm(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))

    # 再描画
    st.experimental_rerun()
