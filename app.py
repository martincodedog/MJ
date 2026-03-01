import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from utils import load_master_data, get_connection

# --- 導入模組化頁面 ---
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history
from views.pro_analysis import show_pro_analysis 
from views.daily_analysis import show_daily_analysis  # <--- 新增這一行

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="G 啦，好想打牌", 
    page_icon="🀄", 
    layout="wide"
)

# --- 2. 常數與全域配置 ---
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
# GID 僅用於 CSV 導出參考，但通常讀取 GSheets 會使用分頁名稱
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. 數據初始化 ---
# 注意：這裡 load_master_data 讀取的是長期累積的 Master Record
df_master = load_master_data(MASTER_SHEET, PLAYERS)

# --- 4. 路由狀態管理 ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 總體概況"

# --- 5. 側邊欄導航 (Sidebar Navigation) ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，雀神終端")
    st.info("量化麻將數據監控系統")
    st.markdown("---")
    
    # 使用按鈕進行頁面切換，並增加圖示美化
    pages = {
        "📊 總體概況": "總體概況",
        "🧮 快速計分": "快速計分",
        "🔍 今日戰局復盤": "今日分析", # <--- 新功能入口
        "🧠 專業量化分析": "專業分析",
        "📜 歷史紀錄回顧": "歷史紀錄"
    }

    for label, target in pages.items():
        if st.button(label, use_container_width=True, type="primary" if st.session_state.page == label else "secondary"):
            st.session_state.page = label
            st.rerun()
        
    st.markdown("---")
    
    # 顯示最後更新日期
    if not df_master.empty:
        try:
            temp_date = pd.to_datetime(df_master['Date'])
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
    # 呼叫剛才寫好的今日分析模組
    show_daily_analysis(PLAYERS)

elif st.session_state.page == "🧠 專業量化分析":
    # 專業分析通常針對長期數據 (Master Record)
    show_pro_analysis(df_master, PLAYERS)

elif st.session_state.page == "📜 歷史紀錄回顧":
    show_history(df_master, PLAYERS)

# --- 7. 全域頁尾 ---
# (選填：可以在此加入版權資訊或版本號)
