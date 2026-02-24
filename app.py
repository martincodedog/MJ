import streamlit as st
import pandas as pd
import numpy as np
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
    
    # Clean Player Columns & handle empty rows
    df = df.dropna(subset=[date_col])
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
    side_df = df[[date_col] + players].copy()
    side_df[date_col] = side_df[date_col].dt.strftime('%Y-%m-%d')
    st.sidebar.dataframe(side_df[::-1], hide_index=True) # Show newest first

    # --- Main App ---
    st.title("🀄 雀神數據分析儀")
    
    # --- 1. Summary Metrics ---
    st.subheader("💰 總結算 (Total Score)")
    cols = st.columns(4)
    for i, p in enumerate(players):
        total = df[p].sum()
        cols[i].metric(label=p, value=f"{total:,.0f}")

    # --- 2. Cumulative Trend ---
    st.subheader("📈 累積走勢")
    chart_data = df.groupby(date_col)[players].sum().cumsum()
    st.line_chart(chart_data)

    st.divider()

    # --- 3. Statistical Prediction (Next Game) ---
    st.subheader("🔮 下場預測 (Next Game Prediction)")
    st.caption("基於最近 5 場表現的加權移動平均值 (Statistical Forecast)")
    
    pred_cols = st.columns(4)
    for i, p in enumerate(players):
        # Get last 5 games
        recent_scores = df[p].tail(5).tolist()
        if len(recent_scores) > 0:
            # Weighted average (recent games have more weight)
            weights = np.arange(1, len(recent_scores) + 1)
            prediction = np.average(recent_scores, weights=weights)
            
            # Form indicator (Is the trend going up or down?)
            delta = prediction - df[p].mean()
            pred_cols[i].metric(label=f"{p} 預測", value=f"{prediction:+.1f}", delta=f"對比平均: {delta:+.1f}")
        else:
            pred_cols[i].write("數據不足")

    st.divider()

    # --- 4. Yearly Summary ---
    st.subheader("🗓️ 年度總結 (Yearly Summary)")
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[players].sum()
    st.table(yearly_df.style.format("{:,.0f}"))

    # --- 5. All Summary Statistics ---
    st.subheader("📊 完整數據匯總 (All Statistics)")
    stats = pd.DataFrame({
        "總分 (Total)": df[players].sum(),
        "平均分 (Avg)": df[players].mean(),
        "標準差 (Volatility)": df[players].std(),
        "最大贏錢 (Max Win)": df[players].max(),
        "最大輸錢 (Max Loss)": df[players].min(),
        "勝率 (Win Rate %)": (df[players] > 0).mean() * 100
    }).T
    st.dataframe(stats.style.format("{:.1f}"), use_container_width=True)

except Exception as e:
    st.error("讀取失敗，請確認 Google Sheet 欄位名稱是否正確。")
    st.exception(e)
