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
    # 更新後的計分表: 3番=$8, 4番=$16, 5番=$48...
    fan_map = {
        3: 8,   # 已修正為 $8
        4: 16, 
        5: 48, 
        6: 64, 
        7: 96, 
        8: 128, 
        9: 192, 
        10: 256
    }
    if fan > 10: return 256
    return fan_map.get(fan, 0)

def get_or_create_worksheet(sheet_name):
    sh = client.open_by_key(SHEET_ID)
    try:
        return sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        new_ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
        return new_ws

@st.cache_data(ttl=10)
def load_master_data():
    df = conn.read(spreadsheet=SHEET_URL, worksheet=MASTER_SHEET).dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'])
    for p in PLAYERS:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df

# --- 4. 介面設計 ---
df = load_master_data()
tabs = st.tabs(["📊 總體概況", "🧮 快速計分", "📜 歷史明細", "🔮 神算預測"])

# --- TAB 1: Dashboard ---
with tabs[0]:
    st.header("💰 雀神累積總結算")
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df[p].sum()
        m_cols[i].metric(label=p, value=f"${total:,.0f}")

    st.divider()
    last_date = df['Date'].max()
    st.subheader(f"📅 上次戰績 ({last_date.strftime('%Y/%m/%d')})")
    last_day = df[df['Date'].dt.date == last_date.date()].copy()
    last_day['Date'] = last_day['Date'].dt.strftime('%Y/%m/%d')
    st.table(last_day[['Martin', 'Lok', 'Stephen', 'Fongka']])

# --- TAB 2: Calculator ---
with tabs[1]:
    today_str = datetime.now().strftime("%Y/%m/%d")
    st.header(f"🧮 今日獨立錄入: {today_str}")
    
    with st.form("pro_calc_form_v4", clear_on_submit=True):
        col_in, col_pre = st.columns([2, 1])
        with col_in:
            winner = st.selectbox("贏家", PLAYERS)
            mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
            loser = st.selectbox("輸家/包家", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
            fan = st.number_input("幾多翻", min_value=3, max_value=13, value=3)
            base = get_base_money(fan)

        with col_pre:
            st.write("##### 💰 損益預覽")
            res = {p: 0 for p in PLAYERS}
            if mode == "出統":
                res[winner], res[loser] = base, -base
            elif mode == "包自摸":
                res[winner], res[loser] = base * 3, -(base * 3)
            else: # 自摸
                res[winner] = base * 3
                for p in PLAYERS:
                    if p != winner: res[p] = -base
            
            for p, v in res.items():
                color = "green" if v > 0 else "red" if v < 0 else "gray"
                st.markdown(f"**{p}**: :{color}[${v:,.0f}]")

        if st.form_submit_button("🚀 提交數據 (自動開新 Tab)", use_container_width=True):
            sheet_tab_name = today_str.replace("/", "-")
            ws_today = get_or_create_worksheet(sheet_tab_name)
            new_row = [datetime.now().strftime("%Y/%m/%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}番"]
            ws_today.append_row(new_row)
            st.success(f"✅ 成功！已存入分頁: {sheet_tab_name}")
            st.balloons()

# --- TAB 3: History ---
with tabs[2]:
    st.header("📜 Master Record 歷史紀錄")
    history_df = df.sort_values(by="Date", ascending=False).copy()
    history_df['Date'] = history_df['Date'].dt.strftime('%Y/%m/%d')
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    st.line_chart(df.set_index("Date")[PLAYERS].cumsum())

# --- TAB 4: Predict ---
with tabs[3]:
    st.header("🔮 下場表現預測")
    p_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        recent = df[p].tail(10).values
        if len(recent) >= 3:
            w = np.arange(1, len(recent) + 1)
            pred = np.average(recent, weights=w)
            p_cols[i].metric(f"{p} 預測得分", f"{pred:+.1f}")
        else:
            p_cols[i].write("數據不足")
