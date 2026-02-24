import streamlit as st
from utils import load_master_data, get_connection
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history

# 配置
st.set_page_config(page_title="G 啦，好想打牌", layout="wide")
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# 初始化
client = get_connection()
df_master = load_master_data(SHEET_URL, "Master Record", PLAYERS)

# Sidebar 導航
if 'page' not in st.session_state:
    st.session_state.page = "快速計分"

with st.sidebar:
    st.markdown("# 🀄 G 啦，好想打牌")
    st.markdown("---")
    if st.button("📊 總體概況", use_container_width=True): st.session_state.page = "總體概況"
    if st.button("🧮 快速計分", use_container_width=True): st.session_state.page = "快速計分"
    if st.button("📜 歷史紀錄", use_container_width=True): st.session_state.page = "歷史紀錄"

# 路由切換
if st.session_state.page == "總體概況":
    show_dashboard(df_master, PLAYERS)
elif st.session_state.page == "快速計分":
    show_calculator(client, SHEET_ID, "Master Record", PLAYERS)
elif st.session_state.page == "歷史紀錄":
    show_history(df_master, PLAYERS)
