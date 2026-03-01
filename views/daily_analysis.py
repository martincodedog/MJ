import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils import SHEET_URL

def show_daily_analysis(players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🔍 今日戰局深度復盤</h2>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type="GSheetsConnection")
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    try:
        # 讀取今日分頁
        df = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
        if df.empty:
            st.info("🐣 今日尚無對局數據，請先前往計分頁錄入。")
            return
    except:
        st.info(f"📅 尚未建立今日 ({today_tab_name}) 的數據表。")
        return

    # --- 1. 戰果總結 (Metrics) ---
    st.subheader("🏆 今日英雄榜")
    today_sums = df[players].sum()
    m_cols = st.columns(4)
    for i, p in enumerate(players):
        val = today_sums[p]
        delta = val # 這裡可以對比上一局，但先以絕對值顯示
        m_cols[i].metric(label=p, value=f"{int(val):+d}", delta=None)

    st.divider()

    # --- 2. 核心行為統計 (技術指標) ---
    st.subheader("⚔️ 行為數據特徵")
    
    # 計算各項指標
    stats_data = []
    for p in players:
        # 贏牌次數
        wins = len(df[df['Winner'] == p])
        # 自摸次數
        tsumo = len(df[(df['Winner'] == p) & (df['Method'] == '自摸')])
        # 出統次數 (放銃)
        feed = len(df[(df['Loser'] == p) & (df['Method'] == '出統')])
        # 被自摸 (不含包牌)
        be_tsumo = len(df[(df['Winner'] != p) & (df['Method'] == '自摸')])
        # 平均贏分 (PL Ratio 基礎)
        p_wins = df[df[p] > 0][p]
        p_losses = df[df[p] < 0][p]
        pl_ratio = (p_wins.mean() / abs(p_losses.mean())) if not p_losses.empty else 0

        stats_data.append({
            "玩家": p,
            "贏牌": wins,
            "自摸": tsumo,
            "放銃(出統)": feed,
            "盈虧比": round(pl_ratio, 2)
        })

    df_stats = pd.DataFrame(stats_data).set_index("玩家")
    
    # 顯示橫向長條圖對比
    st.bar_chart(df_stats[["贏牌", "自摸", "放銃(出統)"]], height=300)
    
    st.markdown("""
    **📝 今日行為解讀：**
    * **贏牌 vs 自摸**：若贏牌多但自摸少，代表今日主要是靠「食胡（抓人放銃）」獲利。
    * **放銃 (出統)**：數值越高，代表今日防守端崩潰，或是運氣極差（點砲）。
    """)

    st.divider()

    # --- 3. 戰局走勢 (Intraday Equity) ---
    st.subheader("📈 今日資產波動走勢")
    # 計算滾動累積損益
    equity_df = df[players].cumsum()
    # 加入第 0 局（起點）
    start_row = pd.DataFrame([[0]*len(players)], columns=players)
    equity_df = pd.concat([start_row, equity_df], ignore_index=True)
    
    st.line_chart(equity_df, height=350)
    
    st.info("這條曲線反映了今日「氣場」的轉移。觀察曲線的斜率，斜率越陡代表該玩家正處於連勝/連敗的爆發期。")

    st.divider()

    # --- 4. 關鍵對局紀錄 (Big Hands) ---
    st.subheader("🔥 今日大牌回顧 (>= 6番)")
    big_hands = df[df['Fan'] >= 6][["Winner", "Loser", "Method", "Fan"]]
    if not big_hands.empty:
        st.table(big_hands)
    else:
        st.write("今日暫無 6 番以上的大牌。")

    # --- 5. 心理熱度警告 (Daily RSI) ---
    st.subheader("⚠️ 短期手感警戒 (今日 RSI)")
    rsi_today = pd.DataFrame()
    for p in players:
        delta = df[p].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=3).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=3).mean()
        rs = gain / (loss + 1e-9)
        rsi_today[p] = 100 - (100 / (1 + rs))
    
    st.line_chart(rsi_today.fillna(50), height=200)
    st.caption("基於今日對局的 RSI (Window=3)。數值超過 80 請注意「過熱回調」，低於 20 請注意「情緒失控」。")
