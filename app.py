import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. 頁面配置
st.set_page_config(page_title="HK Mahjong Master", page_icon="🀄", layout="wide")

# 2. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 定義玩家名單
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]
SHEET_URL = "https://docs.google.com/spreadsheets/d/14yklDMWbghTp47Gl9jFkKyO3CFy6x_el/edit"

@st.cache_data(ttl=60)
def load_data():
    # 讀取數據
    df = conn.read(spreadsheet=SHEET_URL, worksheet="0")
    
    # 判斷日期欄位名稱 (自動識別 'Date' 或第一欄)
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    
    # 確保分數欄位為數字
    for p in PLAYERS:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    
    return df, date_col

try:
    df, date_col = load_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 側邊欄：歷史紀錄 ---
    st.sidebar.header("📜 歷史往績")
    st.sidebar.write(f"最後更新: `{now}`")
    side_df = df[[date_col] + PLAYERS].copy()
    side_df[date_col] = side_df[date_col].dt.strftime('%Y-%m-%d')
    st.sidebar.dataframe(side_df.sort_values(by=date_col, ascending=False), hide_index=True)

    # --- 主介面 ---
    st.title("🀄 香港雀神戰績分析系統")

    # --- 1. 新增數據表單 ---
    with st.expander("➕ 錄入新戰績 (Add New Entry)"):
        with st.form("mahjong_form", clear_on_submit=True):
            f_date = st.date_input("比賽日期", datetime.now())
            c1, c2, c3, c4 = st.columns(4)
            val_m = c
