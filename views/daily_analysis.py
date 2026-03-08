import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils import SHEET_URL
from streamlit_gsheets import GSheetsConnection

def get_hkt():
    return datetime.now(timezone(timedelta(hours=8)))

def show_daily_analysis(players):
    st.markdown("<h2 style='text-align: center;'>🔍 今日戰局深度復盤</h2>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    hkt_now = get_hkt()
    today_tab_name = hkt_now.strftime("%Y-%m-%d")

    try:
        # 分析頁面建議 TTL 設長一點，節省 API 配額
        df = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=20)
        if df.empty or len(df) == 0:
            st.info("🐣 今日尚無對局數據。")
            return
        for p in players:
            df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    except Exception as e:
        st.warning(f"尚未建立今日 ({today_tab_name}) 的數據表或連線受限。")
        return

    # 1. Metrics
    st.subheader("🏆 今日英雄榜")
    sums = df[players].sum()
    m_cols = st.columns(4)
    for i, p in enumerate(players):
        m_cols[i].metric(label=p, value=f"{int(sums[p]):+d}")

    # 2. Chart
    st.subheader("📈 今日資產波動")
    equity = df[players].cumsum()
    zero_row = pd.DataFrame([[0]*len(players)], columns=players)
    equity = pd.concat([zero_row, equity], ignore_index=True)
    st.line_chart(equity)

    # 3. Stats
    st.subheader("⚔️ 行為分析")
    stats = []
    for p in players:
        wins = len(df[df['Winner'] == p])
        feeds = len(df[(df['Loser'] == p) & (df['Method'] == '出統')])
        stats.append({"玩家": p, "贏牌": wins, "放銃": feeds})
    st.bar_chart(pd.DataFrame(stats).set_index("玩家"))

    # 4. Big Hands
    st.subheader("🔥 大牌回顧 (>= 5番)")
    df['Fan'] = pd.to_numeric(df['Fan'], errors='coerce').fillna(0)
    big = df[df['Fan'] >= 5][["Date", "Winner", "Loser", "Method", "Fan"]]
    st.dataframe(big, hide_index=True, use_container_width=True)
