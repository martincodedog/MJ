import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import numpy as np

# 頁面配置
st.set_page_config(page_title="HK Mahjong Master", layout="wide")

# 建立連接
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取數據
@st.cache_data(ttl=60)
def load_and_clean_data():
    players = ["Martin", "Lok", "Stephen", "Fongka"]
    # 這裡放入你的 Google Sheet 編輯連結
    df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/14yklDMWbghTp47Gl9jFkKyO3CFy6x_el/edit", worksheet="Sheet1")
    
    # 清洗數據
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    for p in players:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df, players, date_col

try:
    df, players, date_col = load_and_clean_data()

    # --- 頂部導航與錄入 ---
    st.title("🀄 香港雀神戰績系統")
    
    with st.expander("➕ 錄入新戰績"):
        with st.form("add_form"):
            new_date = st.date_input("日期", datetime.now())
            cols = st.columns(4)
            m = cols[0].number_input("Martin", value=0)
            l = cols[1].number_input("Lok", value=0)
            s = cols[2].number_input("Stephen", value=0)
            f = cols[3].number_input("Fongka", value=0)
            
            if st.form_submit_button("確認提交"):
                if m + l + s + f != 0:
                    st.error("❌ 錯誤：四人得分總和不等於 0，請檢查！")
                else:
                    new_row = pd.DataFrame([{date_col: new_date, "Martin": m, "Lok": l, "Stephen": s, "Fongka": f}])
                    # 更新 Google Sheet (需要配置 secrets)
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/14yklDMWbghTp47Gl9jFkKyO3CFy6x_el/edit", data=updated_df)
                    st.success("✅ 數據已成功同步至 Google Sheets！")
                    st.cache_data.clear()

    # --- 總積分指標 ---
    st.subheader("💰 累積結算")
    m_cols = st.columns(4)
    for i, p in enumerate(players):
        total = df[p].sum()
        m_cols[i].metric(label=p, value=f"{total:,.0f}")

    # --- 下場預測 (加權統計法) ---
    st.divider()
    st.subheader("🔮 下場表現預測")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        recent = df[p].tail(5).values
        if len(recent) > 0:
            # 統計學方法：加權移動平均 (越近期的比賽權重越高)
            weights = np.linspace(0.5, 1.5, len(recent))
            pred = np.average(recent, weights=weights)
            p_cols[i].metric(label=f"{p} 預測", value=f"{pred:+.1f}")

    # --- 年度總結 (附帶冠軍獎盃) ---
    st.divider()
    st.subheader("🗓️ 年度排行榜")
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[players].sum().reset_index()

    def highlight_winners(row):
        # 找出該年度最高分的人
        scores = row[players].astype(float)
        winner = scores.idxmax()
        formatted_row = row.astype(str)
        formatted_row[winner] = f"🏆 {row[winner]:,.0f}"
        return formatted_row

    st.table(yearly_df.apply(highlight_winners, axis=1))

    # --- 所有統計數據 ---
    st.subheader("📊 玩家深度統計")
    all_stats = pd.DataFrame({
        "總分": df[players].sum(),
        "平均": df[players].mean(),
        "單場最高": df[players].max(),
        "單場最低": df[players].min(),
        "勝率 (%)": (df[players] > 0).mean() * 100
    }).T
    st.dataframe(all_stats.style.format("{:.1f}"), use_container_width=True)

except Exception as e:
    st.warning("請在 Streamlit Cloud 的 Secrets 中配置 Google Sheets 的 `service_account` 權限。")
    st.exception(e)
