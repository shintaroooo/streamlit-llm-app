import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# --- ページ設定 ---
st.set_page_config(page_title="専門家AIチャット", layout="centered")
st.title("🧠 専門家AIチャット")

# --- 言語選択 ---
language = st.radio("🌐 Language / 言語を選択してください:", ("日本語", "English"), horizontal=True)

# --- 多言語UI辞書 ---
labels = {
    "日本語": {
        "title": "🧠 専門家AIに相談しよう",
        "instruction": "AIが専門家になりきって、あなたの相談に答えます。専門家を選んで、メッセージを入力してください。",
        "input_placeholder": "メッセージを入力してください",
        "send": "送信",
        "thinking": "AIが回答を考えています...",
        "current_expert": "現在の専門家："
    },
    "English": {
        "title": "🧠 Ask an AI Expert",
        "instruction": "Chat with an AI acting as a domain expert. Select an expert and type your message.",
        "input_placeholder": "Type your message here",
        "send": "Send",
        "thinking": "AI is thinking...",
        "current_expert": "Current Expert:"
    }
}
ui = labels[language]

# --- 専門家選択 ---
expert_type = st.radio("🧑‍🎓 専門家を選んでください:", ("心理カウンセラー", "経営コンサルタント", "パーソナルトレーナー"), key="expert_type")
st.markdown(f"✅ **{ui['current_expert']} {expert_type}**")

# --- セッションステート初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- システムメッセージ生成関数（多言語対応） ---
def get_system_message(expert: str, lang: str) -> str:
    prompts = {
        "日本語": {
            "心理カウンセラー": "あなたは共感力の高い心理カウンセラーです。ユーザーに優しく丁寧に答えてください。",
            "経営コンサルタント": "あなたは戦略的な経営コンサルタントです。論理的にアドバイスしてください。",
            "パーソナルトレーナー": "あなたは前向きなパーソナルトレーナーです。元気づけるアドバイスをしてください。"
        },
        "English": {
            "心理カウンセラー": "You are an empathetic counselor. Respond kindly and attentively.",
            "経営コンサルタント": "You are a strategic business consultant. Give logical, realistic advice.",
            "パーソナルトレーナー": "You are a positive personal trainer. Encourage users with healthy advice."
        }
    }
    return prompts[lang].get(expert, "You are a helpful AI assistant.")

# --- SystemMessage 初期化 or 専門家変更時に更新 ---
system_msg = SystemMessage(content=get_system_message(expert_type, language))
if len(st.session_state.messages) == 0 or (
    isinstance(st.session_state.messages[0], SystemMessage)
    and st.session_state.messages[0].content != system_msg.content
):
    st.session_state.messages = [system_msg]

# --- チャット履歴表示（SystemMessage以外） ---
for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        st.markdown(f"🧑 {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"🤖 {msg.content}")

# --- 入力欄 ---
st.text_input(ui["input_placeholder"], key="user_input")

# --- 送信処理 ---
if st.button(ui["send"]) and st.session_state.user_input.strip() != "":
    user_msg = st.session_state.user_input.strip()
    st.session_state.messages.append(HumanMessage(content=user_msg))

    with st.spinner(ui["thinking"]):
    chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5, streaming=True)
    response = chat.stream(st.session_state.messages)

    # 表示コンテナ
    response_container = st.empty()
    streamed_text = ""

    for chunk in response:
        streamed_text += chunk.text
        response_container.markdown(f"🤖 {streamed_text}")

    # 会話履歴に追加
    st.session_state.messages.append(AIMessage(content=streamed_text))


    # --- 入力欄をリセットして再描画 ---
    st.session_state.user_input = ""
    st.rerun()
