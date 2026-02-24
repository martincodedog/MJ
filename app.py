import streamlit as st
from utils import load_master_data

# Modular views
from views.dashboard import show_dashboard
from views.calculator import show_calculator_csv  # We'll tweak this name
from views.history import show_history

st.set_page_config(page_title="G 啦 (Local)", page_icon="🀄", layout="wide")

PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# Load Data
df_master = load_master_data(PLAYERS)

if 'page' not in st.session_state:
    st.session_state.page = "總體概況"

# Sidebar Navigation (Same as before)
with st.sidebar:
    st.markdown("### 🀄 雀神本地版")
    if st.button("📊 總體概況", use_container_width=True):
        st.session_state.page = "總體概況"
    if st.button("🧮 快速計分", use_container_width=True):
        st.session_state.page = "快速計分"
    if st.button("📜 歷史紀錄", use_container_width=True):
        st.session_state.page = "歷史紀錄"

# Routing
if st.session_state.page == "總體概況":
    show_dashboard(df_master, PLAYERS)
elif st.session_state.page == "快速計分":
    # Pass the save function instead of the Google client
    show_calculator_csv(PLAYERS) 
elif st.session_state.page == "歷史紀錄":
    show_history(df_master, PLAYERS)
