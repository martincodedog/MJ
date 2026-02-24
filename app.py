import streamlit as st
import pandas as pd
import gspread
import numpy as np
from google.oauth2.service_account import Credentials
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(page_title="HK Mahjong Master Pro", page_icon="🀄", layout="wide")

# --- 2. Credentials & Connection ---
creds_dict = st.secrets["connections"]["gsheets"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
MASTER_SHEET = "Master Record"
PLAYERS = ["Martin", "Lok", "Stephen", "Fongka"]

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. Core Functions ---
def get_base_money(fan):
    # Updated: 3 Fan = $8
    fan_map = {3: 8, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
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

@st.cache_data(ttl=5)
def load_master_data():
    df = conn.read(spreadsheet=SHEET_URL, worksheet=MASTER_SHEET).dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'])
    for p in PLAYERS:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df

# --- 4. Load Data ---
df_master = load_master_data()

# --- 5. Interface Tabs ---
tabs = st.tabs(["📊 總體概況", "🧮 快速計分", "📜 歷史明細", "🔮 神算預測"])

# --- TAB 1: Summary Statistics (Dashboard) ---
with tabs[0]:
    st.header("💰 雀神累積總結算")
    
    # Metrics
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df_master[p].sum()
        avg_score = df_master[p].mean()
        m_cols[i].metric(label=f"{p} 總結餘", value=f"${total:,.0f}", delta=f"場均 ${avg_score:.1f}")

    st.divider()

    # Advanced Stats
    st.subheader("📊 玩家深度數據分析")
    summary_list = []
    for p in PLAYERS:
        scores = df_master[p]
        wins = (scores > 0).sum()
        total_games = len(scores)
        summary_list.append({
            "玩家": p,
            "總對局日": total_games,
            "贏錢日數": wins,
            "勝率 (%)": f"{(wins/total_games*100):.1f}%" if total_games > 0 else "0%",
            "單日最高": f"${scores.max():,.0f}",
            "波動穩定度": f"{scores.std():.1f}"
        })
    st.table(pd.DataFrame(summary_list).set_index("玩家"))

    # Last Game Day
    if not df_master.empty:
        last_date = df_master['Date'].max()
        st.subheader(f"📅 最近結算紀錄 ({last_date.strftime('%Y/%m/%d')})")
        last_day_df = df_master[df_master['Date'].dt.date == last_date.date()].copy()
        last_day_df['Date'] = last_day_df['Date'].dt.strftime('%Y/%m/%d')
        # Safety filter for columns
        display_cols = [c for c in (PLAYERS + ['Remark']) if c in last_day_df.columns]
        st.dataframe(last_day_df[display_cols], use_container_width=True, hide_index=True)

# --- TAB 2: Calculator (Daily Record) ---
with tabs[1]:
    today_date_str = datetime.now().strftime("%Y/%m/%d")
    sheet_tab_name = today_date_str.replace("/", "-")
    st.header(f"🧮 今日即時錄入: {today_date_str}")

    # Fetch daily data for real-time total
    try:
        sh = client.open_by_key(SHEET_ID)
        ws_today = sh.worksheet(sheet_tab_name)
        today_raw = ws_today.get_all_records()
        today_df = pd.DataFrame(today_raw) if today_raw else pd.DataFrame(columns=PLAYERS)
        for p in PLAYERS:
            if p in today_df.columns:
                today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
    except:
        today_df = pd.DataFrame(columns=PLAYERS)

    # Real-time Score Preview
    st.subheader("🏆 今日累積總體損益")
    score_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        day_total = today_df[p].sum() if p in today_df.columns else 0
        score_cols[i].metric(label=f"{p} 今日得分", value=f"${day_total:,.0f}")

    st.divider()

    # Form
    with st.form("mahjong_calculator_vfinal", clear_on_submit=True):
        c_in, c_pre = st.columns([2, 1])
        with c_in:
            winner = st.selectbox("贏家 (Winner)", PLAYERS)
            mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
            loser = st.selectbox("誰支付？", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
            fan = st.number_input("翻數", min_value=3, max_value=13, value=3)
            base = get_base_money(fan)
        
        with c_pre:
            st.write("##### 💰 本局計算")
            res = {p: 0 for p in PLAYERS}
            if mode == "出統": res[winner], res[loser] = base, -base
            elif mode == "包自摸": res[winner], res[loser] = base * 3, -(base * 3)
            else: 
                res[winner] = base * 3
                for p in PLAYERS: 
                    if p != winner: res[p] = -base
            for p, v in res.items():
                st.write(f"{p}: {'🟢' if v >= 0 else '🔴'} ${v}")

        if st.form_submit_button("✅ 錄入本局結果", use_container_width=True):
            ws_target = get_or_create_worksheet(sheet_tab_name)
            # Use Remark column as requested
            new_row = [datetime.now().strftime("%Y/%m/%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}番"]
            ws_target.append_row(new_row)
            st.success("本局已成功存入今日分頁！")
            st.rerun()

    # Sync to Master Button
    st.divider()
    if st.button("📤 完場：將今日總分結算至 Master Record", type="primary", use_container_width=True):
        if not today_df.empty and any(p in today_df.columns for p in PLAYERS):
            final_sync_row = [
                today_date_str, 
                int(today_df["Martin"].sum()) if "Martin" in today_df.columns else 0,
