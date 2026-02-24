import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="HK Mahjong Stats", page_icon="🀄", layout="wide")

# 2. Data Loading & Cleaning
SHEET_ID = "14yklDMWbghTp47Gl9jFkKyO3CFy6x_el"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300) # Refresh data every 5 minutes
def get_data():
    df = pd.read_csv(URL)
    players = ["Martin", "Lok", "Stephen", "Fongka"]
    
    # Clean Date Column (Assumes column name is 'Date' or '日期')
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    
    # Clean Player Columns
    for p in players:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
            
    return df, players, date_col

try:
    df, players, date_col = get_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Sidebar: Historic Results ---
    st.sidebar.header("📜 歷史往績 (History)")
    st.sidebar.write(f"最後更新: `{now}`")
    
    # Create a simplified view for the sidebar
    history_display = df[[date_col] + players].copy()
    st.sidebar.dataframe(history_display, hide_index=True)

    # --- Main App ---
    st.title("🀄 雀神戰績表")
    st.info(f"數據已更新於: {now}")

    # --- Summary Metrics ---
    st.subheader("💰 總結算 (Total Score)")
    cols = st.columns(4)
    for i, p in enumerate(players):
        total = df[p].sum()
        # Highlight winner in green, loser in red
        color = "normal" if total >= 0 else "inverse"
        cols[i].metric(label=p, value=f"{total:,.0f}")

    st.divider()

    # --- Cumulative Trend with Date X-Axis ---
    st.subheader("📈 累積走勢 (Cumulative Trend)")
    
    # Prepare data for line chart
    # We group by date in case multiple games happen on the same day
    chart_data = df.groupby(date_col)[players].sum().cumsum()
    
    # Streamlit's native line chart uses the index as the X-axis
    st.line_chart(chart_data)

    # --- Performance Summary Table ---
    st.subheader("📊 數據摘要 (Summary)")
    summary_df = pd.DataFrame({
        "玩家": players,
        "總分": [df[p].sum() for p in players],
        "平均每場": [df[p].mean() for p in players],
        "最高得分": [df[p].max() for p in players],
        "最低得分": [df[p].min() for p in players]
    })
    st.table(summary_df)

except Exception as e:
    st.error("讀取失敗。請確保 Google Sheet 的第一欄是日期，且列名包含 Martin, Lok, Stephen, Fongka。")
    st.exception(e)
