import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. 頁面配置 ---
st.set_page_config(page_title="HK Mahjong Master", page_icon="🀄", layout="wide")

# --- 2. 參數與連線 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]
WORKSHEET_NAME = "Sheet1" # 確保與 Google Sheet 名稱一致

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 計錢邏輯 Function ---
def get_base_money(fan):
    # 你的自定義計分表
    fan_map = {
        3: 4, 4: 16, 5: 48, 6: 64, 
        7: 96, 8: 128, 9: 192, 10: 256
    }
    if fan > 10: return 256
    return fan_map.get(fan, 0)

@st.cache_data(ttl=10)
def load_data():
    df = conn.read(spreadsheet=SHEET_URL, worksheet=WORKSHEET_NAME)
    df = df.dropna(how='all')
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    for p in PLAYERS:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df, date_col

# --- 4. 主程式介面 ---
df, date_col = load_data()

# 使用 Tabs 將功能分開
tab_dashboard, tab_calculator = st.tabs(["📊 數據總結 (Dashboard)", "🧮 自動計錢入賬 (Calculator)"])

# --- TAB 1: 數據總結 ---
with tab_dashboard:
    st.header("累積戰績總覽")
    
    # 總分卡片
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total_score = df[p].sum()
        m_cols[i].metric(label=p, value=f"${total_score:,.0f}")

    st.divider()
    
    # 年度排行榜
    st.subheader("🗓️ 年度排行榜")
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[PLAYERS].sum().reset_index()
    
    def add_trophy(row):
        scores = row[PLAYERS].astype(float)
        winner = scores.idxmax()
        formatted = row.astype(str)
        formatted[winner] = f"🏆 {row[winner]:,.0f}"
        return formatted

    if not yearly_df.empty:
        st.table(yearly_df.apply(add_trophy, axis=1))

    # 走勢圖
    st.subheader("📈 累積走勢")
    trend_data = df.groupby(date_col)[PLAYERS].sum().cumsum()
    st.line_chart(trend_data)

# --- TAB 2: 自動計錢入賬 ---
with tab_calculator:
    st.header("🧮 即時計分錄入")
    
    with st.form("mahjong_calc_form", clear_on_submit=True):
        f_date = st.date_input("比賽日期", datetime.now())
        
        col_input, col_preview = st.columns([2, 1])
        
        with col_input:
            winner = st.selectbox("贏家 (Winner)", PLAYERS)
            mode = st.radio("食糊方式", ["出統 (食客付)", "自摸 (三家付)", "包自摸 (一人包)"], horizontal=True)
            
            if mode == "出統 (食客付)":
                loser = st.selectbox("誰出沖？", [p for p in PLAYERS if p != winner])
            elif mode == "包自摸 (一人包)":
                loser =
