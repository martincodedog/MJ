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

# Streamlit 原生連線 (用於快速讀取)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. 核心功能函式 ---
def get_base_money(fan):
    # 3番=$8, 4番=$16, 5番=$48, 6番=$64, 7番=$96, 8番=$128, 9番=$192, 10番=$256
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

# --- 4. 數據加載 ---
df_master = load_master_data()

# --- 5. 介面 Tabs ---
tabs = st.tabs(["📊 總體概況", "🧮 快速計分", "📜 歷史明細", "🔮 神算預測"])

# --- TAB 1: 總體概況 (Dashboard) ---
with tabs[0]:
    st.header("💰 雀神累積總結算")
    
    # A. 頂部核心指標
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df_master[p].sum()
        avg_score = df_master[p].mean()
        m_cols[i].metric(label=f"{p} 總分", value=f"${total:,.0f}", delta=f"場均 ${avg_score:.1f}")

    st.divider()

    # B. 進階統計摘要
    st.subheader("📊 玩家深度數據分析")
    summary_list = []
    for p in PLAYERS:
        scores = df_master[p]
        wins = (scores > 0).sum()
        total_games = len(scores)
        summary_list.append({
            "玩家": p,
            "總場次": total_games,
            "勝場": wins,
            "勝率 (%)": f"{(wins/total_games*100):.1f}%" if total_games > 0 else "0%",
            "場均得分": f"{scores.mean():.1f}",
            "生涯最高": f"${scores.max():,.0f}",
            "波動度 (Std)": f"{scores.std():.1f}"
        })
    st.table(pd.DataFrame(summary_list).set_index("玩家"))

    # C. 最近一次戰績
    last_date = df_master['Date'].max()
    st.subheader(f"📅 最近結算紀錄 ({last_date.strftime('%Y/%m/%d')})")
    last_day = df_master[df_master['Date'].dt.date == last_date.date()].copy()
    last_day['Date'] = last_day['Date'].dt.strftime('%Y/%m/%d')
    st.dataframe(last_day[PLAYERS + ['Remark']], use_container_width=True)

# --- TAB 2: 快速計分 (Calculator) ---
with tabs[1]:
    today_date_str = datetime.now().strftime("%Y/%m/%d")
    sheet_tab_name = today_date_str.replace("/", "-")
    st.header(f"🧮 今日即時計分: {today_date_str}")

    # 讀取今日數據以顯示即時總計
    try:
        sh = client.open_by_key(SHEET_ID)
        ws_today = sh.worksheet(sheet_tab_name)
        today_df = pd.DataFrame(ws_today.get_all_records())
        for p in PLAYERS:
            today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
    except:
        today_df = pd.DataFrame(columns=PLAYERS)

    # 損益預覽：今日總分
    st.subheader("🏆 今日累積戰報")
    score_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        day_total = today_df[p].sum() if not today_df.empty else 0
        score_cols[i].metric(label=f"{p} 今日總計", value=f"${day_total:,.0f}")

    st.divider()

    # 輸入表單
    with st.form("mahjong_form_final", clear_on_submit=True):
        c_in, c_pre = st.columns([2, 1])
        with c_in:
            winner = st.selectbox("贏家 (Winner)", PLAYERS)
            mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
            if mode != "自摸":
                loser = st.selectbox("誰出沖/包牌？", [p for p in PLAYERS if p != winner])
            else:
                loser = "三家"
            fan = st.number_input("幾多翻？", min_value=3, max_value=13, value=3)
            base = get_base_money(fan)
        
        with c_pre:
            st.write("##### 💰 本局預計損益")
            res = {p: 0 for p in PLAYERS}
            if mode == "出統": res[winner], res[loser] = base, -base
            elif mode == "包自摸": res[winner], res[loser] = base * 3, -(base * 3)
            else: 
                res[winner] = base * 3
                for p in PLAYERS: 
                    if p != winner: res[p] = -base
            for p, v in res.items():
                st.write(f"{p}: {'🟢' if v >=0 else '🔴'} ${v}")

        if st.form_submit_button("✅ 錄入本局", use_container_width=True):
            ws_target = get_or_create_worksheet(sheet_tab_name)
            new_row = [datetime.now().strftime("%Y/%m/%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}番"]
            ws_target.append_row(new_row)
            st.success("本局已存入今日分頁！")
            st.rerun()

    # 結算按鈕
    st.divider()
    if st.button("📤 結束今日對局：結算至 Master Record", type="primary", use_container_width=True):
        if not today_df.empty:
            final_row = [
                today_date_str, 
                int(today_df["Martin"].sum()), 
                int(today_df["Lok"].sum()), 
                int(today_df["Stephen"].sum()), 
                int(today_df["Fongka"].sum()), 
                f"Sync from {sheet_tab_name}"
            ]
            ws_master = sh.worksheet(MASTER_SHEET)
            ws_master.append_row(final_row)
            st.success("🎉 今日戰績已成功結算至 Master Record 總表！")
            st.cache_data.clear()
        else:
            st.error("今日尚無數據，無法結算。")

# --- TAB 3: 歷史明細 ---
with tabs[2]:
    st.header("📜 全歷史紀錄 (Master Record)")
    history_view = df_master.sort_values(by="Date", ascending=False).copy()
    history_view['Date'] = history_view['Date'].dt.strftime('%Y/%m/%d')
    st.dataframe(history_view, use_container_width=True, hide_index=True)
    
    st.subheader("📈 累積走勢圖")
    st.line_chart(df_master.set_index("Date")[PLAYERS].cumsum())

# --- TAB 4: 神算預測 ---
with tabs[3]:
    st.header("🔮 下場表現預測 (WMA)")
    p_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        recent = df_master[p].tail(10).values
        if len(recent) >= 3:
            w = np.arange(1, len(recent) + 1)
            pred = np.average(recent, weights=w)
            p_cols[i].metric(f"{p} 預期得分", f"{pred:+.1f}")
            status = "🔥 旺門" if pred > 20 else "🧊 冷門" if pred < -20 else "⚖️ 平穩"
            p_cols[i].write(f"狀態: {status}")
        else:
            p_cols[i].write("需要至少 3 局數據")
