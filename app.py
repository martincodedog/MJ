import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="HK Mahjong Stats", page_icon="🀄")

# 2. Data Loading
# Replacing /edit with /export?format=csv to get the raw data
SHEET_ID = "14yklDMWbghTp47Gl9jFkKyO3CFy6x_el"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600) # Refresh every 10 mins
def get_data():
    df = pd.read_csv(URL)
    # Ensure columns match your Excel: Martin, Lok, Stephen, Fongka
    players = ["Martin", "Lok", "Stephen", "Fongka"]
    # Clean data: convert to numeric and fill empty as 0
    for p in players:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df, players

try:
    df, players = get_data()

    st.title("🀄 雀神戰績表")
    st.caption("數據同步自 Google Sheets")

    # --- Summary Metrics ---
    st.subheader("💰 總結算 (Total)")
    m1, m2, m3, m4 = st.columns(4)
    cols = [m1, m2, m3, m4]

    for i, p in enumerate(players):
        total = df[p].sum()
        cols[i].metric(label=p, value=f"{total:,.0f}")

    st.divider()

    # --- Cumulative Trend (Line Chart) ---
    st.subheader("📈 走勢圖 (Cumulative)")
    cumulative_df = df[players].cumsum()
    # Streamlit native line chart
    st.line_chart(cumulative_df)

    # --- Win/Loss Analysis (Bar Chart) ---
    st.subheader("📊 每場勝負 (Per Game)")
    st.bar_chart(df[players])

    # --- Raw Data ---
    with st.expander("查看原始數據記錄"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("讀取失敗。請確保 Google Sheet 已開啟「知道連結的任何人都可以查看」。")
    st.info(f"Debug Info: {e}")
