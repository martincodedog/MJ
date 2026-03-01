import streamlit as st
import pandas as pd
from utils import load_master_data, SHEET_URL # 確保 utils 有定義 SHEET_URL

# 導入模組化分頁
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
# 注意：為了配合 utils 裡的 pd.read_csv，我們必須使用 /export?format=csv 格式
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
# 指定 Master Record 分頁的 GID (請確認你的 Master Record 分頁 GID 是否為 0)
MASTER_GID = "0" 
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={MASTER_GID}"

MASTER_SHEET_NAME = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# --- 3. 數據初始化 ---
# 使用你的 utils.py 函數，傳入 CSV 導出網址
df_master = load_master_data(CSV_URL, MASTER_SHEET_NAME, PLAYERS)

# --- 4. 路由狀態管理 ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 總體概況"

# --- 5. 側邊欄導航 ---
with st.sidebar:
    st.markdown("# 🀄 G 啦，雀神終端")
    st.info("量化麻將數據監控系統")
    st.markdown("---")
    
    # 定義按鈕導覽
    nav_items = {
        "📊 總體概況": "dashboard",
        "🧮 快速計分": "calculator",
        "🔍 今日戰局復盤": "daily",
        "🧠 專業量化分析": "pro",
        "📜 歷史紀錄回顧": "history"
    }

    for label in nav_items.keys():
        if st.button(label, use_container_width=True, 
                     type="primary" if st.session_state.page == label else "secondary"):
            st.session_state.page = label
            st.rerun()
        
    st.markdown("---")
    
    # 顯示最後更新日期 (加上安全性檢查防止 KeyError)
    if not df_master.empty:
        if 'Date' in df_master.columns:
            try:
                # 取得最後一行日期
                last_entry = df_master['Date'].iloc[-1]
                # 如果是 Timestamp 物件則格式化，如果是字串則直接顯示
                last_date_str = last_entry.strftime('%Y-%m-%d') if hasattr(last_entry, 'strftime') else str(last_entry)
                st.caption(f"📅 數據同步至: {last_date_str}")
            except:
                st.caption("📅 數據已同步")
        else:
            st.warning("⚠️ CSV 未偵測到 Date 欄位")
            # 偵錯用：顯示目前抓到的欄位
            # st.write(df_master.columns)
    else:
        st.caption("📅 暫無歷史紀錄 (Master 為空)")

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
    # 傳入歷史數據進行 PL Ratio, Skewness, RSI 等量化計算
    show_pro_analysis(df_master, PLAYERS)

elif st.session_state.page == "📜 歷史紀錄回顧":
    show_history(df_master, PLAYERS)
