import streamlit as st
from streamlit_gsheets import GSheetsConnection
from utils import load_master_data, get_connection

# Import your modular views
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="G 啦，好想打牌", 
    page_icon="🀄", 
    layout="wide"
)

# --- 2. Constants & Global Config ---
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. Data & Connection Initialization ---
# Get GSpread client for writing and GSheetsConnection for fast reading
client = get_connection()
df_master = load_master_data(SHEET_URL, MASTER_SHEET, PLAYERS)

# --- 4. Session State Management (Routing) ---
# FIX: Set default page to "總體概況" to make it the landing page
if 'page' not in st.session_state:
    st.session_state.page = "總體概況"

# --- 5. Sidebar Navigation ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，好想打牌")
    st.info("專業雀神數據監控系統")
    st.markdown("---")
    
    # Navigation Buttons
    if st.button("📊 總體概況", use_container_width=True):
        st.session_state.page = "總體概況"
        st.rerun()
        
    if st.button("🧮 快速計分", use_container_width=True):
        st.session_state.page = "快速計分"
        st.rerun()
        
    if st.button("📜 歷史紀錄", use_container_width=True):
        st.session_state.page = "歷史紀錄"
        st.rerun()
        
    st.markdown("---")
    st.caption(f"Last Sync: {df_master['Date'].max().strftime('%Y-%m-%d') if not df_master.empty else 'N/A'}")

# --- 6. Page Routing Logic ---
# This part decides which file from /views to display
if st.session_state.page == "總體概況":
    show_dashboard(df_master, PLAYERS)

elif st.session_state.page == "快速計分":
    show_calculator(client, SHEET_ID, MASTER_SHEET, PLAYERS)

elif st.session_state.page == "歷史紀錄":
    show_history(df_master, PLAYERS)

# --- 7. Global Footer ---
st.sidebar.markdown("---")
st.sidebar.write("Developed for the Mahjong Masters.")
