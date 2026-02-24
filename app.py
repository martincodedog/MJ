import streamlit as st
from utils import load_master_data
from views.dashboard import show_dashboard
from views.calculator import show_calculator

st.set_page_config(page_title="雀神監控 G 啦", page_icon="🀄", layout="wide")

PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# 每次 Refresh 都重新攞 Sheet 啲數
df_master = load_master_data()

if 'page' not in st.session_state:
    st.session_state.page = "邊個係水魚？🎣"

with st.sidebar:
    st.markdown("### 🀄 雀神雲端版")
    if st.button("🎣 邊個係水魚？", width='stretch'):
        st.session_state.page = "邊個係水魚？🎣"
        st.rerun()
    if st.button("🧮 快速填數", width='stretch'):
        st.session_state.page = "快速計分"
        st.rerun()

if st.session_state.page == "邊個係水魚？🎣":
    show_dashboard(df_master, PLAYERS)
elif st.session_state.page == "快速計分":
    show_calculator(PLAYERS)
