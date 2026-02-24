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

# --- 3. Functions ---
def get_base_money(fan):
    fan_map = {3: 8, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
    return fan_map.get(fan, 256 if fan > 10 else 0)

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

# --- 4. Modern Sidebar Navigation (No Radio Buttons) ---
if 'page' not in st.session_state:
    st.session_state.page = "快速計分"  # Default landing page

with st.sidebar:
    st.title("🀄 HK Mahjong Master")
    st.markdown("---")
    if st.button("📊 總體概況", use_container_width=True):
        st.session_state.page = "總體概況"
    if st.button("🧮 快速計分", use_container_width=True):
        st.session_state.page = "快速計分"
    if st.button("📜 歷史紀錄", use_container_width=True):
        st.session_state.page = "歷史紀錄"
    st.markdown("---")
    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")

# Load Master Data
df_master = load_master_data()

# --- 5. Page Routing ---

# --- PAGE: 總體概況 ---
if st.session_state.page == "總體概況":
    st.header("📊 總結算 & 下場預測")
    
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df_master[p].sum()
        recent = df_master[p].tail(7).values
        pred_text = "N/A"
        if len(recent) >= 3:
            w = np.arange(1, len(recent) + 1)
            pred = np.average(recent, weights=w)
            pred_text = f"{pred:+.1f}"
        m_cols[i].metric(label=f"{p} 總結算", value=f"${total:,.0f}", delta=f"預測: {pred_text}")

    st.divider()
    st.subheader("📈 累積走勢圖")
    st.line_chart(df_master.set_index("Date")[PLAYERS].cumsum())

    st.divider()
    st.subheader("📋 表現分析")
    summary_list = []
    for p in PLAYERS:
        scores = df_master[p]
        wins = (scores > 0).sum()
        summary_list.append({
            "玩家": p,
            "勝率 (%)": f"{(wins/len(scores)*100):.1f}%" if len(scores) > 0 else "0%",
            "場均得分": f"{scores.mean():.1f}",
            "生涯最高": f"${scores.max():,.0f}"
        })
    st.table(pd.DataFrame(summary_list).set_index("玩家"))

# --- PAGE: 快速計分 ---
elif st.session_state.page == "快速計分":
    today_date_str = datetime.now().strftime("%Y/%m/%d")
    sheet_tab_name = today_date_str.replace("/", "-")
    st.header(f"🧮 今日對局: {today_date_str}")

    try:
        sh = client.open_by_key(SHEET_ID)
        ws_today = sh.worksheet(sheet_tab_name)
        today_df = pd.DataFrame(ws_today.get_all_records())
        for p in PLAYERS: today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
    except:
        today_df = pd.DataFrame(columns=["Date"] + PLAYERS + ["Remark"])

    st.markdown(f"### 🏆 今日即時累積")
    cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        cols[i].markdown(f"**{p}**: `${today_df[p].sum():,.0f}`")

    st.divider()
    col_in, col_pre = st.columns([1, 1])
    with col_in:
        st.markdown("#### 📝 錄入數據")
        winner = st.selectbox("贏家", PLAYERS)
        mode = st.radio("食糊方式", ["出統", "自摸", "包自摸"], horizontal=True)
        loser = st.selectbox("誰付錢？", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
        fan = st.select_slider("翻數", options=list(range(3, 11)), value=3)
        base = get_base_money(fan)

    with col_pre:
        st.markdown("#### 🧐 預覽寫入")
        res = {p: 0 for p in PLAYERS}
        if mode == "出統": res[winner], res[loser] = base, -base
        elif mode == "包自摸": res[winner], res[loser] = base * 3, -(base * 3)
        else: 
            res[winner] = base * 3
            for p in PLAYERS: 
                if p != winner: res[p] = -base
        
        preview_row = {**{p: [res[p]] for p in PLAYERS}, "備註": [f"{winner} {mode} {fan}番"]}
        st.table(pd.DataFrame(preview_row))

    if st.button("🚀 確認錄入此局", use_container_width=True):
        ws_target = get_or_create_worksheet(sheet_tab_name)
        new_row = [datetime.now().strftime("%Y/%m/%d %H:%M"), res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], f"{winner} {mode} {fan}番"]
        ws_target.append_row(new_row)
        st.success("✅ 數據已寫入")
        st.rerun()

    st.divider()
    if st.button("📤 結算並覆寫 Master Record", type="primary", use_container_width=True):
        if not today_df.empty:
            ws_master = sh.worksheet(MASTER_SHEET)
            all_data = ws_master.get_all_values()
            rows_to_keep = [all_data[0]]
            for row in all_data[1:]:
                if row[0] != today_date_str: rows_to_keep.append(row)
            
            summary_row = [
                today_date_str, 
                int(today_df["Martin"].sum()), int(today_df["Lok"].sum()), 
                int(today_df["Stephen"].sum()), int(today_df["Fongka"].sum()), 
                f"Auto-Sync: {sheet_tab_name}"
            ]
            rows_to_keep.append(summary_row)
            ws_master.clear()
            ws_master.update('A1', rows_to_keep)
            st.success("🎊 總表結算完成！")
            st.cache_data.clear()
        else:
            st.error("今日暫無數據。")

# --- PAGE: 歷史紀錄 ---
elif st.session_state.page == "歷史紀錄":
    st.header("📜 歷史紀錄 (Martin / Lok / Stephen / Fongka)")
    st.dataframe(df_master[PLAYERS].sort_index(ascending=False), use_container_width=True)
