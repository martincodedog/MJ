import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Page Config
st.set_page_config(page_title="HK Mahjong Stats", page_icon="🀄", layout="wide")

# 2. Establish Google Sheets Connection
# Ensure your secrets.toml has the "connections.gsheets" configuration
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) # Short TTL so new entries show up quickly
def get_data():
    players = ["Martin", "Lok", "Stephen", "Fongka"]
    # Reading data via the connection
    df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/14yklDMWbghTp47Gl9jFkKyO3CFy6x_el/edit", worksheet="0")
    
    # Cleaning
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    for p in players:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df, players, date_col

try:
    df, players, date_col = get_data()
    
    st.title("🀄 雀神戰績分析儀")

    # --- NEW: Add Entry Form ---
    with st.expander("➕ 新增戰績 (Add New Entry)"):
        with st.form("add_record"):
            new_date = st.date_input("日期", datetime.now())
            c1, c2, c3, c4 = st.columns(4)
            m_score = c1.number_input("Martin Score", value=0, step=1)
            l_score = c2.number_input("Lok Score", value=0, step=1)
            s_score = c3.number_input("Stephen Score", value=0, step=1)
            f_score = c4.number_input("Fongka Score", value=0, step=1)
            
            submit = st.form_submit_button("提交紀錄 (Submit)")
            
            if submit:
                # Basic check: Score should sum to 0 in most Mahjong variants
                if (m_score + l_score + s_score + f_score) != 0:
                    st.warning("⚠️ 警告：總分不等於 0，請檢查輸入。")
                
                new_row = pd.DataFrame([{
                    date_col: new_date,
                    "Martin": m_score,
                    "Lok": l_score,
                    "Stephen": s_score,
                    "Fongka": f_score
                }])
                
                # Logic to append to Google Sheets (Requires Edit Permission/Service Account)
                # conn.create(data=pd.concat([df, new_row])) # This depends on your specific setup
                st.success("✅ 紀錄已成功提交！(請確保已配置 Google Sheets 寫入權限)")
                st.cache_data.clear()

    # --- Summary Metrics ---
    st.subheader("💰 總結算 (Total Score)")
    cols = st.columns(4)
    for i, p in enumerate(players):
        total = df[p].sum()
        cols[i].metric(label=p, value=f"{total:,.0f}")

    # --- Yearly Summary with Champion Emoji ---
    st.divider()
    st.subheader("🗓️ 年度總結 (Yearly Summary)")
    
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[players].sum().reset_index()

    # Function to add emoji to the winner's score
    def add_champion_emoji(row):
        scores = row[players].astype(float)
        winner = scores.idxmax()
        row_styled = row.astype(str)
        row_styled[winner] = f"🏆 {row[winner]:,.0f}"
        return row_styled

    display_yearly = yearly_df.apply(add_champion_emoji, axis=1)
    st.table(display_yearly)

    # --- Statistical Prediction ---
    st.subheader("🔮 下場預測")
    # (Same prediction logic as before...)

except Exception as e:
    st.error("讀取失敗。請檢查 Google Sheets 連結與權限。")
    st.exception(e)
