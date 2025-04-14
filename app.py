import streamlit as st
from langchain.chat_models import ChatOpenAI  # Correct import
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# --- ページ設定 ---
st.set_page_config(page_title="専門家AIチャット", layout="centered")
st.title("専門家AIチャットアプリ")

st.markdown("""
このアプリでは、AIが選んだ専門家になりきってあなたの相談に答えてくれます。  
お好きな専門家を選んで、メッセージを送ってみましょう！
""")

# --- セッションステートで履歴管理（初期化） ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 専門家選択（途中で切り替え可能） ---
expert_type = st.radio(
    "🧑‍🎓 相談したい専門家を選んでください：",
    ("心理カウンセラー", "経営コンサルタント", "パーソナルトレーナー"),
    key="expert_type"
)

st.markdown(f"✅ **現在の専門家：{expert_type}**")

# --- システムメッセージ生成 ---
def get_system_message(expert: str) -> str:
    prompts = {
        "心理カウンセラー": "あなたは共感力の高いプロの心理カウンセラーです。ユーザーの悩みに対して優しく、丁寧に寄り添ってください。",
        "経営コンサルタント": "あなたは戦略的な経営コンサルタントです。ビジネスの課題に対して的確で論理的なアドバイスを提供してください。",
        "パーソナルトレーナー": "あなたは前向きで明るいパーソナルトレーナーです。健康や運動に関する相談に、元気づけるように答えてください。"
    }
    return prompts.get(expert, "あなたは親切なAIアシスタントです。")

# --- 専門家変更 or 初回にSystemMessageを差し替え ---
if len(st.session_state.messages) == 0 or (
    isinstance(st.session_state.messages[0], SystemMessage) and
    st.session_state.messages[0].content != get_system_message(expert_type)
):
    st.session_state.messages = [SystemMessage(content=get_system_message(expert_type))]

# --- チャット履歴の表示 ---
for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        st.markdown(f"🧑 あなた：{msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"🤖 AI（{expert_type}）：{msg.content}")

# --- 入力フォーム ---
user_input = st.text_input("💬 メッセージを入力してください", key="user_input")

if st.button("送信") and user_input.strip() != "":
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.spinner("AIが回答を考えています..."):
        chat = ChatOpenAI(model_name="gpt-4", temperature=0.5)  # Use a valid model name
        response = chat(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))
    st.experimental_rerun()
