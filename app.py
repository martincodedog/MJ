import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. 頁面配置 ---
st.set_page_config(page_title="HK Mahjong Master", page_icon="🀄", layout="wide")

# --- 2. 參數設定 ---
# 使用你轉換後的原生 Google Sheets 連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]
# 請確認你的分頁名稱，預設通常是 "Sheet1" 或 "工作表1"
WORKSHEET_NAME = "Sheet1" 

# 建立連線 (會自動抓取 Secrets 中的憑證)
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    try:
        # 讀取指定分頁
        df = conn.read(spreadsheet=SHEET_URL, worksheet=WORKSHEET_NAME)
        
        # 清理空列並處理日期
        df = df.dropna(how='all')
        date_col = 'Date' if 'Date' in df.columns else df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])
        
        # 確保分數欄位是數字
        for p in PLAYERS:
            if p in df.columns:
                df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
        return df, date_col
    except Exception as e:
        st.error(f"讀取失敗：請檢查分頁名稱是否為 '{WORKSHEET_NAME}'，或 Service Account 權限。")
        st.stop()

# --- 3. 執行讀取 ---
df, date_col = load_data()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- 4. 側邊欄：歷史紀錄與更新資訊 ---
st.sidebar.header("📜 歷史往績")
st.sidebar.caption(f"最後更新日期: {now}")
side_df = df[[date_col] + PLAYERS].copy()
side_df[date_col] = side_df[date_col].dt.strftime('%Y-%m-%d')
st.sidebar.dataframe(side_df.sort_values(by=date_col, ascending=False), hide_index=True)

# --- 5. 主介面：新增戰績表單 ---
st.title("🀄 香港雀神戰績分析系統")

with st.expander("➕ 錄入新戰績 (Add New Entry)", expanded=False):
    with st.form("mahjong_form", clear_on_submit=True):
        f_date = st.date_input("比賽日期", datetime.now())
        c1, c2, c3, c4 = st.columns(4)
        val_m = c1.number_input("Martin", step=1, value=0)
        val_l = c2.number_input("Lok", step=1, value=0)
        val_s = c3.number_input("Stephen", step=1, value=0)
        val_f = c4.number_input("Fongka", step=1, value=0)
        
        submit_btn = st.form_submit_button("提交數據至 Google Sheets")
        
        if submit_btn:
            # 1. 檢查分數是否平衡
            total_sum = val_m + val_l + val_s + val_f
            if total_sum != 0:
                st.error(f"❌ 錯誤：目前總分為 {total_sum}。四人得分總和必須等於 0！")
            else:
                # 2. 準備新數據
                new_entry = pd.DataFrame({
                    date_col: [pd.to_datetime(f_date)],
                    "Martin": [val_m],
                    "Lok": [val_l],
                    "Stephen": [val_s],
                    "Fongka": [val_f]
                })
                # 3. 讀取最新狀態並合併
                latest_df = conn.read(spreadsheet=SHEET_URL, worksheet=WORKSHEET_NAME)
                updated_df = pd.concat([latest_df, new_entry], ignore_index=True)
                
                # 4. 寫入回 Google Sheets
                conn.update(spreadsheet=SHEET_URL, worksheet=WORKSHEET_NAME, data=updated_df)
                st.success("✅ 數據已成功同步！")
                st.cache_data.clear() # 清除緩存以顯示新數據
                st.rerun()

# --- 6. 核心統計與圖表 ---

# 第一部分：總得分卡片
st.subheader("💰 累積總結算")
m_cols = st.columns(4)
for i, p in enumerate(PLAYERS):
    total_score = df[p].sum()
    m_cols[i].metric(label=p, value=f"{total_score:,.0f}")

# 第二部分：下場表現預測
st.divider()
st.subheader("🔮 下場表現預測 (Forecast)")
st.caption("基於最近 5 場表現的加權移動平均值 (Weighted Moving Average)")
p_cols = st.columns(4)
for i, p in enumerate(PLAYERS):
    recent_scores = df[p].tail(5).values
    if len(recent_scores) > 0:
        weights = np.arange(1, len(recent_scores) + 1)
        prediction = np.average(recent_scores, weights=weights)
        p_cols[i].metric(label=f"{p} 預期得分", value=f"{prediction:+.1f}")
    else:
        p_cols[i].write("數據不足")

# 第三部分：年度排行榜 (含冠軍 🏆)
st.divider()
st.subheader("🗓️ 年度排行榜 (Yearly Summary)")
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

# 第四部分：走勢圖與深度數據
st.subheader("📊 數據摘要與走勢")
tab1, tab2 = st.tabs(["累積走勢圖", "深度統計表"])

with tab1:
    trend_data = df.groupby(date_col)[PLAYERS].sum().cumsum()
    st.line_chart(trend_data)

with tab2:
    full_stats = pd.DataFrame({
        "總分": df[PLAYERS].sum(),
        "平均分": df[PLAYERS].mean(),
        "單場最高": df[PLAYERS].max(),
        "勝率 (%)": (df[PLAYERS] > 0).mean() * 100
    }).T
    st.dataframe(full_stats.style.format("{:.1f}"), use_container_width=True)
