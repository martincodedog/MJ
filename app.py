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

# --- 3. 核心功能 ---
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

# --- 4. Sidebar 導航 (加入 Master Title) ---
if 'page' not in st.session_state:
    st.session_state.page = "快速計分"

with st.sidebar:
    st.markdown(f"# 🀄 G 啦，好想打牌") # 你的專屬標題
    st.markdown("---")
    if st.button("📊 總體概況", use_container_width=True):
        st.session_state.page = "總體概況"
    if st.button("🧮 快速計分", use_container_width=True):
        st.session_state.page = "快速計分"
    if st.button("📜 歷史紀錄", use_container_width=True):
        st.session_state.page = "歷史紀錄"
    st.markdown("---")

df_master = load_master_data()

# --- 5. 頁面內容 ---

# --- 頁面 1: 總體概況 (專業統計版) ---
if st.session_state.page == "總體概況":
    st.header("📊 專業數據分析系統")
    
    # A. 頂部核心指標
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        total = df_master[p].sum()
        # 加權預測 (最近對局比重較高)
        recent = df_master[p].tail(5).values
        pred_val = np.average(recent, weights=np.arange(1, len(recent)+1)) if len(recent) >= 3 else 0
        
        m_cols[i].metric(
            label=f"{p} 累積結餘", 
            value=f"${total:,.0f}", 
            delta=f"趨勢預測: {pred_val:+.1f}",
            delta_color="normal"
        )

    st.divider()

    # B. 累積走勢圖
    st.subheader("📈 歷史戰鬥力走勢")
    st.line_chart(df_master.set_index("Date")[PLAYERS].cumsum())

    # C. 專業統計表
    st.divider()
    st.subheader("📋 核心表現摘要 (KPIs)")
    
    stats_df = []
    for p in PLAYERS:
        p_data = df_master[p]
        wins = (p_data > 0).sum()
        total_days = len(p_data)
        
        stats_df.append({
            "玩家": p,
            "對局總天數": total_days,
            "勝場 (贏錢日)": wins,
            "勝率 (Win Rate)": f"{(wins/total_days*100):.1f}%" if total_days > 0 else "0%",
            "場均盈虧 (Avg)": f"${p_data.mean():.1f}",
            "最大單日盈利": f"${p_data.max():,.0f}",
            "最大單日虧損": f"${p_data.min():,.0f}",
            "風險值 (波動率)": f"{p_data.std():.1f}"
        })
    
    # 顯示美化後的表格
    st.table(pd.DataFrame(stats_df).set_index("玩家"))

# --- 頁面 2: 快速計分 ---
elif st.session_state.page == "快速計分":
    today_date_str = datetime.now().strftime("%Y/%m/%d")
    sheet_tab_name = today_date_str.replace("/", "-")
    st.header(f"🧮 今日對局錄入: {today_date_str}")

    try:
        sh = client.open_by_key(SHEET_ID)
        ws_today = sh.worksheet(sheet_tab_name)
        today_df = pd.DataFrame(ws_today.get_all_records())
        for p in PLAYERS: today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
    except:
        today_df = pd.DataFrame(columns=["Date"] + PLAYERS + ["Remark"])

    st.markdown("### 🏆 今日即時累計")
    m_cols = st.columns(4)
    for i, p in enumerate(PLAYERS):
        day_val = today_df[p].sum() if p in today_df.columns else 0
        m_cols[i].metric(label=p, value=f"${day_val:,.0f}")

    st.divider()
    col_in, col_pre = st.columns([1, 1])
    with col_in:
        st.markdown("#### 📝 錄入數據")
        winner = st.selectbox("贏家", PLAYERS)
        mode = st.radio("方式", ["出統", "自摸", "包自摸"], horizontal=True)
        loser = st.selectbox("誰支付？", [p for p in PLAYERS if p != winner]) if mode != "自摸" else "三家"
        fan = st.select_slider("翻數", options=list(range(3, 11)), value=3)
        base = get_base_money(fan)

    with col_pre:
        st.markdown("#### 🧐 預覽寫入內容")
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
        st.success("✅ 數據已寫入今日分頁")
        st.rerun()

    st.divider()
    if st.button("📤 結算並覆寫 Master Record", type="primary", use_container_width=True):
        if not today_df.empty:
            ws_master = sh.worksheet(MASTER_SHEET)
            all_data = ws_master.get_all_values()
            rows_to_keep = [all_data[0]]
            for row in all_data[1:]:
                if row[0] != today_date_str: rows_to_keep.append(row)
            
            summary_row = [today_date_str, int(today_df["Martin"].sum()), int(today_df["Lok"].sum()), int(today_df["Stephen"].sum()), int(today_df["Fongka"].sum()), f"Sync: {sheet_tab_name}"]
            rows_to_keep.append(summary_row)
            ws_master.clear()
            ws_master.update('A1', rows_to_keep)
            st.success("🎊 總表結算完成！")
            st.cache_data.clear()
        else:
            st.error("今日暫無數據。")

# --- 頁面 3: 歷史紀錄 ---
elif st.session_state.page == "歷史紀錄":
    st.header("📜 歷史得分紀錄")
    history_display = df_master.set_index("Date")[PLAYERS].sort_index(ascending=False)
    history_display.index = history_display.index.strftime('%Y/%m/%d')
    st.dataframe(history_display, use_container_width=True)
