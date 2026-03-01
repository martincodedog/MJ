import streamlit as st
import pandas as pd
from utils import load_master_data

# --- 1. 頁面配置 ---
st.set_page_config(
    page_title="G 啦，好想打牌", 
    page_icon="🀄", 
    layout="wide"
)

# --- 2. 常數與全域配置 ---
# 這是你的 Spreadsheet ID
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"

# 重點：Master Record 的 GID 必須是 2131114078 (根據你提供的連結)
# 並且網址必須是 /export?format=csv 才能讓 pd.read_csv 讀到正確的欄位
MASTER_GID = "2131114078" 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={MASTER_GID}"

PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. 數據初始化 ---
# 呼叫你 utils.py 裡的 load_master_data
df_master = load_master_data(CSV_URL, "Master Record", PLAYERS)

# --- 4. 路由狀態管理 ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 總體概況"

# --- 5. 側邊欄導航 ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，雀神終端")
    st.info("量化麻將數據監控系統")
    st.markdown("---")
    
    # 導覽按鈕
    if st.button("📊 總體概況", use_container_width=True, type="primary" if st.session_state.page == "📊 總體概況" else "secondary"):
        st.session_state.page = "📊 總體概況"
        st.rerun()
        
    if st.button("🧮 快速計分", use_container_width=True, type="primary" if st.session_state.page == "🧮 快速計分" else "secondary"):
        st.session_state.page = "🧮 快速計分"
        st.rerun()

    if st.button("🔍 今日戰局復盤", use_container_width=True, type="primary" if st.session_state.page == "🔍 今日戰局復盤" else "secondary"):
        st.session_state.page = "🔍 今日戰局復盤"
        st.rerun()

    if st.button("🧠 專業量化分析", use_container_width=True, type="primary" if st.session_state.page == "🧠 專業量化分析" else "secondary"):
        st.session_state.page = "🧠 專業量化分析"
        st.rerun()
        
    if st.button("📜 歷史紀錄", use_container_width=True, type="primary" if st.session_state.page == "📜 歷史紀錄" else "secondary"):
        st.session_state.page = "📜 歷史紀錄"
        st.rerun()

    st.markdown("---")
    
    # --- Debug 與 日期顯示 ---
    if not df_master.empty:
        # 如果欄位名稱還是連在一起，這裡會印出錯誤
        if 'Date' in df_master.columns:
            try:
                last_date = df_master['Date'].iloc[-1].strftime('%Y-%m-%d')
                st.caption(f"📅 數據同步至: {last_date}")
            except:
                st.caption(f"📅 數據讀取成功")
        else:
            st.error("❌ CSV 欄位解析失敗")
            # 輔助偵錯：顯示目前讀到的第一個欄位名稱是什麼
            st.write(f"目前讀到的標題是: {df_master.columns[0]}")
    else:
        st.warning("⚠️ 無法載入數據，請檢查權限")

# --- 6. 導入視圖 (Views) ---
# 注意：這些 function 需在對應的 views/ 檔案中定義
from views.dashboard import show_dashboard
from views.calculator import show_calculator
from views.history import show_history
from views.pro_analysis import show_pro_analysis 
from views.daily_analysis import show_daily_analysis

if st.session_state.page == "📊 總體概況":
    show_dashboard(df_master, PLAYERS)
elif st.session_state.page == "🧮 快速計分":
    show_calculator(PLAYERS)
elif st.session_state.page == "🔍 今日戰局復盤":
    show_daily_analysis(PLAYERS)
elif st.session_state.page == "🧠 專業量化分析":
    show_pro_analysis(df_master, PLAYERS)
elif st.session_state.page == "📜 歷史紀錄":
    show_history(df_master, PLAYERS)
