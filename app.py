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
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit?gid=2131114078#gid=2131114078"

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
            val_m = c1.number_input("Martin", step=1, value=0)
            val_l = c2.number_input("Lok", step=1, value=0)
            val_s = c3.number_input("Stephen", step=1, value=0)
            val_f = c4.number_input("Fongka", step=1, value=0)
            
            submit_btn = st.form_submit_button("提交數據至 Google Sheets")
            
            if submit_btn:
                # 檢查分數是否平衡 (四人總和必須為 0)
                total_sum = val_m + val_l + val_s + val_f
                if total_sum != 0:
                    st.error(f"❌ 錯誤：總分為 {total_sum}。四人得分總和必須等於 0！")
                else:
                    # 建立新列
                    new_entry = pd.DataFrame({
                        date_col: [pd.to_datetime(f_date)],
                        "Martin": [val_m],
                        "Lok": [val_l],
                        "Stephen": [val_s],
                        "Fongka": [val_f]
                    })
                    # 合併並更新
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, data=updated_df)
                    st.success("✅ 數據已成功寫入 Google Sheets！")
                    st.cache_data.clear()
                    st.rerun()

    # --- 2. 總結算指標 ---
    st.subheader("💰 累積總結算")
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total_score = df[p].sum()
        m_cols[i].metric(label=p, value=f"{total_score:,.0f}")

    # --- 3. 下場表現預測 ---
    st.divider()
    st.subheader("🔮 統計學預測 (Next Game Forecast)")
    st.caption("基於最近 5 場表現的加權移動平均值")
    p_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        recent_scores = df[p].tail(5).values
        if len(recent_scores) > 0:
            # 權重：最近的場次權重較高 [1, 2, 3, 4, 5]
            w = np.arange(1, len(recent_scores) + 1)
            prediction = np.average(recent_scores, weights=w)
            p_cols[i].metric(label=f"{p} 預期得分", value=f"{prediction:+.1f}")
        else:
            p_cols[i].write("數據不足")

    # --- 4. 年度總結 (含冠軍 Emoji) ---
    st.divider()
    st.subheader("🗓️ 年度排行榜 (Yearly Summary)")
    
    df['Year'] = df[date_col].dt.year
    yearly_df = df.groupby('Year')[PLAYERS].sum().reset_index()

    def get_champion_style(row):
        scores = row[PLAYERS].astype(float)
        winner = scores.idxmax()
        formatted = row.astype(str)
        # 加上冠軍獎盃
        formatted[winner] = f"🏆 {row[winner]:,.0f}"
        return formatted

    styled_yearly = yearly_df.apply(get_champion_style, axis=1)
    st.table(styled_yearly)

    # --- 5. 累積走勢圖 ---
    st.subheader("📈 戰績走勢圖")
    trend_data = df.groupby(date_col)[PLAYERS].sum().cumsum()
    st.line_chart(trend_data)

    # --- 6. 完整深度統計 ---
    st.divider()
    st.subheader("📊 全方位數據匯總")
    full_stats = pd.DataFrame({
        "總分 (Total)": df[PLAYERS].sum(),
        "平均分 (Average)": df[PLAYERS].mean(),
        "波動性 (Volatility)": df[PLAYERS].std(),
        "勝率 (Win Rate %)": (df[PLAYERS] > 0).mean() * 100,
        "最大單場贏錢": df[PLAYERS].max(),
        "最大單場輸錢": df[PLAYERS].min()
    }).T
    st.dataframe(full_stats.style.format("{:.1f}"), use_container_width=True)

except Exception as e:
    st.error("App 運行出錯。")
    st.info("請檢查：1. Secrets 是否配置正確；2. Google Sheet 是否已分享給 Service Account；3. 欄位名稱是否正確。")
    st.exception(e)
