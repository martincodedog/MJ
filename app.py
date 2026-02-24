import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. 頁面配置 ---
st.set_page_config(page_title="HK Mahjong Master", page_icon="🀄", layout="wide")

# --- 2. 認證與連線 ---
# 從 Streamlit Secrets 讀取憑證 (用於 gspread 開新 Tab)
creds_dict = st.secrets["connections"]["gsheets"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# 檔案資訊
SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

# Streamlit 原生連線 (用於快速讀取)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 功能函式 ---
def get_base_money(fan):
    fan_map = {3: 4, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
    return fan_map.get(fan, 256 if fan > 10 else 0)

def get_or_create_worksheet(sheet_name):
    sh = client.open_by_key(SHEET_ID)
    try:
        return sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # 如果找不到，就開一個新 Tab
        new_ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        # 初始化標題
        new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
        return new_ws

# --- 4. 主介面 ---
tab_dashboard, tab_calculator = st.tabs(["📊 總體數據", "🧮 每日錄入 (自動開表)"])

# --- TAB 1: Dashboard ---
with tab_dashboard:
    df = conn.read(spreadsheet=SHEET_URL, worksheet=MASTER_SHEET).dropna(how='all')
    st.header("累積戰績 (Master Record)")
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        m_cols[i].metric(label=p, value=f"${pd.to_numeric(df[p]).sum():,.0f}")
    st.divider()
    st.line_chart(df.set_index("Date")[PLAYERS].apply(pd.to_numeric).cumsum())

# --- TAB 2: Calculator ---
with tab_calculator:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.header(f"今日對局錄入: {today_str}")

    with st.form("calc_form", clear_on_submit=True):
        col_input, col_preview = st.columns([2, 1])
        with col_input:
            winner = st.selectbox("贏家", PLAYERS)
            mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
            loser = st.selectbox("輸家/包家", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
            fan = st.number_input("翻數", min_value=3, max_value=13, value=3)
            base_money = get_base_money(fan)
        
        with col_preview:
            st.write("##### 💰 本局損益預覽")
            res = {p: 0 for p in PLAYERS}
            if mode == "出統": res[winner], res[loser] = base_money, -base_money
            elif mode == "包自摸": res[winner], res[loser] = base_money * 3, -(base_money * 3)
            else: 
                res[winner] = base_money * 3
                for p in PLAYERS: 
                    if p != winner: res[p] = -base_money
            for p, v in res.items():
                st.write(f"{p}: {'🟢' if v >=0 else '🔴'} ${v}")

        if st.form_submit_button("✅ 提交並同步 (自動開新 Tab)"):
            # 1. 寫入每日 Tab (自動創建)
            ws_today = get_or_create_worksheet(today_str)
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}番"]
            ws_today.append_row(new_row)
            
            # 2. 同步寫入 Master Record
            ws_master = client.open_by_key(SHEET_ID).worksheet(MASTER_SHEET)
            ws_master.append_row(new_row)
            
            st.success(f"成功！已在 Google Sheet 開啟/更新分頁: {today_str}")
            st.balloons()
