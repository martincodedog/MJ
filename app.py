import streamlit as st
import pandas as pd  # 確保有 import pandas 處理日期
from streamlit_gsheets import GSheetsConnection
from utils import load_master_data, get_connection

# Import your modular views
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history
from views.pro_analysis import show_pro_analysis 

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="G 啦，好想打牌", 
    page_icon="🀄", 
    layout="wide"
)

# --- 2. Constants & Global Config ---
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
# 使用確切的 gid 2131114078，並移除 export 中的 sheet name 避免空格衝突
GID = "2131114078"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. Data & Connection Initialization ---
df_master = load_master_data(SHEET_URL, MASTER_SHEET, PLAYERS)

# --- 4. Session State Management (Routing) ---
if 'page' not in st.session_state:
    st.session_state.page = "總體概況"

# --- 5. Sidebar Navigation ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，好想打牌")
    st.info("專業雀神數據監控系統")
    st.markdown("---")
    
    if st.button("📊 總體概況", use_container_width=True):
        st.session_state.page = "總體概況"
        st.rerun()
        
    if st.button("🧮 快速計分", use_container_width=True):
        st.session_state.page = "快速計分"
        st.rerun()

    if st.button("🧠 專業數據分析", use_container_width=True):
        st.session_state.page = "專業分析"
        st.rerun()
        
    if st.button("📜 歷史紀錄", use_container_width=True):
        st.session_state.page = "歷史紀錄"
        st.rerun()
        
    st.markdown("---")
    
    # 顯示最後更新日期 (修正了 pd 未定義可能產生的錯誤)
    if not df_master.empty:
        try:
            # 轉換為日期格式以獲取最大值
            temp_date = pd.to_datetime(df_master['Date'])
            last_date = temp_date.max().strftime('%Y-%m-%d')
            st.caption(f"Last Sync: {last_date}")
        except:
            st.caption(f"Last Sync: {df_master['Date'].iloc[-1]}")

# --- 6. Page Routing Logic ---
if st.session_state.page == "總體概況":
    show_dashboard(df_master, PLAYERS)

elif st.session_state.page == "快速計分":
    show_calculator(PLAYERS)

elif st.session_state.page == "專業分析":
    show_pro_analysis(df_master, PLAYERS)

elif st.session_state.page == "歷史紀錄":
    show_history(df_master, PLAYERS)

# --- 7. Global Footer ---
st.sidebar.markdown("---")
st.sidebar.write("Developed for the Mahjong Masters.")
