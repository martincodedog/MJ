import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from utils import SHEET_URL

def get_hong_kong_time():
    """獲取當前香港時間 (UTC+8)"""
    return datetime.now(timezone(timedelta(hours=8)))

def show_daily_analysis(players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🔍 今日戰局深度復盤</h2>", unsafe_allow_html=True)
    
    # 1. 取得香港日期
    hk_now = get_hong_kong_time()
    today_tab_name = hk_now.strftime("%Y-%m-%d")
    
    # 使用 ttl=10 減少分析頁面頻繁刷新導致的 API 配額爆掉
    conn = st.connection("gsheets", type="GSheetsConnection")

    try:
        # 讀取今日分頁
        df = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=10)
        
        # 檢查是否為空或是只有 Header
        if df.empty or len(df) == 0:
            st.info(f"🐣 香港時間 {today_tab_name} 尚無對局數據。")
            return
            
        # 數據清洗：確保玩家欄位是數值，防止計算錯誤
        for p in players:
            if p in df.columns:
                df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
            else:
                # 如果找不到玩家欄位，補上 0
                df[p] = 0
                
    except Exception as e:
        if "429" in str(e):
            st.error("🚨 Google API 讀取太頻繁（配額限制），請等候 30 秒再刷新。")
        else:
            st.info(f"📅 尚未建立今日 ({today_tab_name}) 的數據表或連線不穩定。")
        return

    # --- 1. 戰果總結 (Metrics) ---
    st.subheader("🏆 今日英雄榜")
    today_sums = df[players].sum()
    m_cols = st.columns(4)
    for i, p in enumerate(players):
        val = today_sums[p]
        m_cols[i].metric(label=p, value=f"{int(val):+d}")

    st.divider()

    # --- 2. 核心行為統計 ---
    st.subheader("⚔️ 行為數據特徵")
    
    stats_data = []
    for p in players:
        # 贏牌次數 (Winner 欄位匹配)
        wins = len(df[df['Winner'] == p])
        # 自摸次數 (贏家是自己且方式是自摸/包自摸)
        tsumo = len(df[(df['Winner'] == p) & (df['Method'].isin(['自摸', '包自摸']))])
        # 放銃次數 (輸家是自己且方式是出統)
        feed = len(df[(df['Loser'] == p) & (df['Method'] == '出統')])
        
        # 盈虧比計算 (平均贏分 / 平均輸分)
        p_wins = df[df[p] > 0][p]
        p_losses = df[df[p] < 0][p]
        pl_ratio = (p_wins.mean() / abs(p_losses.mean())) if not p_losses.empty and p_losses.mean() != 0 else 0

        stats_data.append({
            "玩家": p,
            "贏牌": wins,
            "自摸": tsumo,
            "放銃(出統)": feed,
            "盈虧比": round(pl_ratio, 2)
        })

    df_stats = pd.DataFrame(stats_data).set_index("玩家")
    st.bar_chart(df_stats[["贏牌", "自摸", "放銃(出統)"]], height=300)

    st.divider()

    # --- 3. 戰局走勢 (累積盈虧) ---
    st.subheader("📈 今日資產波動走勢")
    # 計算累積損益
    equity_df = df[players].cumsum()
    # 增加初始點 0
    zero_start = pd.DataFrame([[0]*len(players)], columns=players)
    equity_df = pd.concat([zero_start, equity_df], ignore_index=True)
    
    st.line_chart(equity_df, height=350)
    st.caption("觀察曲線斜率：越陡代表該玩家氣勢正盛或連續大敗。")

    st.divider()

    # --- 4. 大牌回顧 ---
    # 根據你的新賠率，5番以上已經很痛，這裡過濾 5 番以上的紀錄
    st.subheader("🔥 今日大牌回顧 (>= 5番)")
    if 'Fan' in df.columns:
        df['Fan'] = pd.to_numeric(df['Fan'], errors='coerce').fillna(0)
        big_hands = df[df['Fan'] >= 5][["Date", "Winner", "Loser", "Method", "Fan"]]
        if not big_hands.empty:
            st.dataframe(big_hands, hide_index=True, use_container_width=True)
        else:
            st.write("今日暫無 5 番以上的大牌。")

    # --- 5. 短期狀態 RSI ---
    st.subheader("⚠️ 今日手感 RSI")
    rsi_today = pd.DataFrame()
    # 窗口設為 3 局，反映當前手熱不熱
    window = 3
    for p in players:
        delta = df[p].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / (loss + 1e-9)
        rsi_today[p] = 100 - (100 / (1 + rs))
    
    st.line_chart(rsi_today.fillna(50), height=200)
    st.caption(f"基於最近 {window} 局表現。80 以上過熱，20 以下低潮。")
