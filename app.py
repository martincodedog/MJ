import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from utils import load_master_data, get_connection

# --- 導入模組化頁面 ---
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history
from views.pro_analysis import show_pro_analysis 
from views.daily_analysis import show_daily_analysis

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="G 啦，好想打牌", 
    page_icon="🀄", 
    layout="wide"
)

# --- 2. 常數與全域配置 ---
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
# 這裡定義基礎 URL，供 load_master_data 使用
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. 數據初始化 (修正點在此) ---
# 確保傳入 3 個 positional arguments: URL, Worksheet Name, Players List
df_master = load_master_data(SHEET_URL, MASTER_SHEET, PLAYERS)

# --- 4. 路由狀態管理 ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 總體概況"

# --- 5. 側邊欄導航 ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，雀神終端")
    st.info("量化麻將數據監控系統")
    st.markdown("---")
    
    # 定義按鈕與其對應的內部標籤
    nav_options = {
        "📊 總體概況": "總體概況",
        "🧮 快速計分": "快速計分",
        "🔍 今日戰局復盤": "今日分析",
        "🧠 專業量化分析": "專業分析",
        "📜 歷史紀錄回顧": "歷史紀錄"
    }

    for label in nav_options.keys():
        if st.button(label, use_container_width=True, 
                     type="primary" if st.session_state.page == label else "secondary"):
            st.session_state.page = label
            st.rerun()
        
    st.markdown("---")
    
    # 顯示最後更新日期 (從 df_master 提取)
    if not df_master.empty:
        try:
            # 轉換為日期格式以獲取最大值
            temp_date = pd.to_datetime(df_master['Date'], errors='coerce')
            last_date = temp_date.max().strftime('%Y-%m-%d')
            st.caption(f"📅 數據同步至: {last_date}")
        except:
            st.caption(f"📅 最後紀錄: {df_master['Date'].iloc[-1]}")

    st.markdown("---")
    st.write("Developed for Mahjong Masters.")

# --- 6. 頁面路由邏輯 ---
if st.session_state.page == "📊 總體概況":
    show_dashboard(df_master, PLAYERS)

elif st.session_state.page == "🧮 快速計分":
    show_calculator(PLAYERS)

elif st.session_state.page == "🔍 今日戰局復盤":
    show_daily_analysis(PLAYERS)

elif st.session_state.page == "🧠 專業量化分析":
    # 專業量化分析需要用到長期數據 df_master 來計算 Skewness 和 Rolling Sharpe
    show_pro_analysis(df_master, PLAYERS)

elif st.session_state.page == "📜 歷史紀錄回顧":
    show_history(df_master, PLAYERS)
