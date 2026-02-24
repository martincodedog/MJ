import streamlit as st
import pandas as pd
import gspread
import numpy as np
from google.oauth2.service_account import Credentials
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. 頁面配置 ---
st.set_page_config(page_title="HK Mahjong Master Pro", page_icon="🀄", layout="wide")

# --- 2. 認證與連線 ---
creds_dict = st.secrets["connections"]["gsheets"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 核心功能函式 ---
def get_base_money(fan):
    fan_map = {3: 4, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
    return fan_map.get(fan, 256 if fan > 10 else 0)

def get_or_create_worksheet(sheet_name):
    sh = client.open_by_key(SHEET_ID)
    try:
        return sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        new_ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
        return new_ws

@st.cache_data(ttl=10)
def load_all_data():
    df = conn.read(spreadsheet=SHEET_URL, worksheet=MASTER_SHEET).dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'])
    for p in PLAYERS:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df

# --- 4. 介面設計 (Tabs) ---
df = load_all_data()
tabs = st.tabs(["📊 總體概況", "🧮 快速計分", "📜 歷史明細", "🔮 神算預測"])

# --- TAB 1: Dashboard (Master Record Summary) ---
with tabs[0]:
    st.header("💰 雀神總結算")
    
    # A. 總結統計
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df[p].sum()
        m_cols[i].metric(label=p, value=f"${total:,.0f}", delta=f"Avg: {df[p].mean():.1f}")

    st.divider()
    
    # B. 深度統計表
    st.subheader("📊 深度數據分析")
    stats_df = pd.DataFrame({
        "總得分": df[PLAYERS].sum(),
        "平均得分": df[PLAYERS].mean(),
        "最高贏錢": df[PLAYERS].max(),
        "最高輸錢": df[PLAYERS].min(),
        "食糊次數": (df[PLAYERS] > 0).sum(),
        "勝率 (%)": (df[PLAYERS] > 0).mean() * 100
    }).T
    st.dataframe(stats_df.style.format("{:.1f}"), use_container_width=True)

    # C. Last Game Day Record
    st.divider()
    last_date = df['Date'].max()
    st.subheader(f"📅 上次戰績 ({last_date.strftime('%Y-%m-%d')})")
    last_day_df = df[df['Date'].dt.date == last_date.date()]
    st.table(last_day_df)

# --- TAB 2: Calculator (自動開表寫入) ---
with tabs[1]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.header(f"🧮 今日錄入: {today_str}")
    
    with st.form("calc_form_final", clear_on_submit=True):
        col_in, col_pre = st.columns([2, 1])
        with col_in:
            winner = st.selectbox("贏家", PLAYERS)
            mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
            loser = st.selectbox("輸家/包家", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
            fan = st.number_input("幾多番", min_value=3, max_value=13, value=3)
            base = get_base_money(fan)
        
        with col_pre:
            st.write("##### 💰 損益預覽")
            res = {p: 0 for p in PLAYERS}
            if mode == "出統": res[winner], res[loser] = base, -base
            elif mode == "包自摸": res[winner], res[loser] = base * 3, -(base * 3)
            else: 
                res[winner] = base * 3
                for p in PLAYERS: 
                    if p != winner: res[p] = -base
            for p, v in res.items():
                st.write(f"{p}: {'🟢' if v >=0 else '🔴'} ${v}")

        if st.form_submit_button("✅ 提交並同步 (自動建立今日 Tab)"):
            ws_today = get_or_create_worksheet(today_str)
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}翻"]
            ws_today.append_row(new_row)
            ws_master = client.open_by_key(SHEET_ID).worksheet(MASTER_SHEET)
            ws_master.append_row(new_row)
            st.success("數據已同步至今日分頁及總表！")
            st.cache_data.clear()
            st.rerun()

# --- TAB 3: History (所有分頁紀錄) ---
with tabs[2]:
    st.header("📜 全歷史明細")
    # 顯示所有 Master Record 的數據，最新排最前
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
    
    # 累積走勢圖
    st.subheader("📈 累積走勢")
    st.line_chart(df.set_index("Date")[PLAYERS].cumsum())

# --- TAB 4: Predict (統計預測) ---
with tabs[3]:
    st.header("🔮 下場表現預測")
    st.info("基於統計學加權移動平均法 (Weighted Moving Average) 計算近期氣勢。")
    
    pred_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        # 取得最近 10 次的成績
        recent_data = df[p].tail(10).values
        if len(recent_data) >= 3:
            # 權重越近越高
            weights = np.arange(1, len(recent_data) + 1)
            prediction = np.average(recent_data, weights=weights)
            
            # 計算波動性
            volatility = np.std(recent_data)
            
            pred_cols[i].metric(label=f"{p} 預期得分", value=f"{prediction:+.1f}")
            
            if prediction > 20: status = "🔥 氣勢如虹"
            elif prediction > 0: status = "📈 穩步上揚"
            elif prediction < -20: status = "🧊 進入冰封"
            else: status = "⚖️ 表現平穩"
            
            pred_cols[i].write(f"**狀態:** {status}")
            pred_cols[i].caption(f"波動值: {volatility:.1f}")
        else:
            pred_cols[i].write("數據不足 (需要至少 3 局)")
