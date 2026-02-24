import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="HK Mahjong Stats", page_icon="🀄", layout="wide")

# 2. Data Loading & Cleaning
SHEET_ID = "14yklDMWbghTp47Gl9jFkKyO3CFy6x_el"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def get_data():
    df = pd.read_csv(URL)
    players = ["Martin", "Lok", "Stephen", "Fongka"]
    
    # Clean Date Column
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    
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
    
    # Sidebar view (formatted date for display)
    side_df = df[[date_col] + players].copy()
    side_df[date_col] = side_df[date_col].dt.strftime('%Y-%m-%d')
    st.sidebar.dataframe(side_df, hide_index=True)

    # --- Main App ---
    st.title("🀄 雀神戰績表")
    st.info(f"數據已同步: {now}")

    # --- 1. Summary Metrics ---
    st.subheader("💰 總結算 (Total Score)")
    cols = st.columns(4)
    for i, p in enumerate(players):
        total = df[p].sum()
        cols[i].metric(label=p, value=f"{total:,.0f}")

    st.divider()

    # --- 2. Cumulative Trend ---
    st.subheader("📈 累積走勢 (Cumulative Trend)")
    # Group by date for the chart
    chart_data = df.groupby(date_col)[players].sum().cumsum()
    st.line_chart(chart_data)

    st.divider()

    # --- 3. Yearly Summary (New Section) ---
    st.subheader("🗓️ 年度總結 (Yearly Summary)")
    
    # Create Year column
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[players].sum()
    
    # Add a "Yearly Winner" logic
    def highlight_winner(s):
        is_max = s == s.max()
        return ['background-color: #d4edda; font-weight: bold' if v else '' for v in is_max]

    # Display as a styled table
    st.dataframe(
        yearly_df.style.apply(highlight_winner, axis=1).format("{:,.0f}"),
        use_container_width=True
    )

    # Optional: Yearly Bar Chart
    st.bar_chart(yearly_df)

except Exception as e:
    st.error("讀取失敗。請確保 Excel 格式正確。")
    st.exception(e)
