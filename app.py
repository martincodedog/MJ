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
        # 自動建立新分頁 (當日紀錄)
        new_ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
        return new_ws

@st.cache_data(ttl=10)
def load_master_data():
    # 僅讀取，不寫入
    df = conn.read(spreadsheet=SHEET_URL, worksheet=MASTER_SHEET).dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'])
    for p in PLAYERS:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df

# --- 4. 介面設計 ---
df = load_master_data()
tabs = st.tabs(["📊 總體概況", "🧮 快速計分", "📜 歷史明細", "🔮 神算預測"])

# --- TAB 1: Dashboard (唯讀自 Master Record) ---
with tabs[0]:
    st.header("💰 雀神總結算 (唯讀自總表)")
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df[p].sum()
        m_cols[i].metric(label=p, value=f"${total:,.0f}")

    st.divider()
    st.subheader("📊 深度數據分析")
    stats_df = pd.DataFrame({
        "總得分": df[PLAYERS].sum(),
        "平均得分": df[PLAYERS].mean(),
        "最高單場": df[PLAYERS].max(),
        "勝率 (%)": (df[PLAYERS] > 0).mean() * 100
    }).T
    st.dataframe(stats_df.style.format("{:.1f}"), use_container_width=True)

    last_date = df['Date'].max()
    st.subheader(f"📅 最近一次戰績紀錄 ({last_date.strftime('%Y-%m-%d')})")
    st.table(df[df['Date'].dt.date == last_date.date()])

# --- TAB 2: Calculator (只寫入當天新表，不碰 Master Record) ---
with tabs[1]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.header(f"🧮 今日獨立錄入: {today_str}")
    st.warning("⚠️ 此處錄入的數據僅會儲存在當日分頁，不會自動同步至 Master Record。")
    
    with st.form("calc_form_new_tab", clear_on_submit=True):
        col_in, col_pre = st.columns([2, 1])
        with col_in:
            winner = st.selectbox("贏家", PLAYERS)
            mode = st.radio("方式", ["出統", "自摸", "包自摸"], horizontal=True)
            loser = st.selectbox("輸家/包家", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
            fan = st.number_input("翻數", min_value=3, max_value=13, value=3)
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

        if st.form_submit_button("✅ 提交至當日分頁", use_container_width=True):
            # 僅寫入當日 Tab
            ws_today = get_or_create_worksheet(today_str)
            new_row = [datetime.now().strftime("%Y-%m-%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}翻"]
            ws_today.append_row(new_row)
            
            st.success(f"成功！數據已存入 Google Sheet 新分頁: {today_str}")
            st.info("若需更新總表，請手動將數據複製到 Master Record。")

# --- TAB 3: History ---
with tabs[2]:
    st.header("📜 Master Record 歷史紀錄")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
    st.line_chart(df.set_index("Date")[PLAYERS].cumsum())

# --- TAB 4: Predict ---
with tabs[3]:
    st.header("🔮 基於 Master Record 的預測")
    pred_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        recent_data = df[p].tail(10).values
        if len(recent_data) >= 3:
            weights = np.arange(1, len(recent_data) + 1)
            prediction = np.average(recent_data, weights=weights)
            pred_cols[i].metric(label=f"{p} 預期得分", value=f"{prediction:+.1f}")
        else:
            pred_cols[i].write("數據不足")
