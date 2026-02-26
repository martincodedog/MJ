import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h3 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計 (精簡版)</h3>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足，無法生成進階風險圖表。")
        return

    # 基礎數據準備
    player_data_dict = {p: pd.to_numeric(df_master[p], errors='coerce').fillna(0) for p in players}

    # --- 1. 小型化損益分佈圖 (保持原有功能) ---
    st.subheader("📊 損益密度矩陣 (-500 ~ +500)")
    bins = [-float('inf'), -500, -300, -100, 0, 100, 300, 500, float('inf')]
    labels = ["<-500", "-300", "-100", "<0", ">0", "+100", "+300", ">500"]

    chart_cols = st.columns(2)
    for i, p in enumerate(players):
        with chart_cols[i % 2]:
            st.markdown(f"<p style='margin-bottom:-10px; font-size:14px; font-weight:bold; color:#2E86C1;'>● {p} 分佈</p>", unsafe_allow_html=True)
            dist_df = pd.cut(player_data_dict[p], bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
            st.bar_chart(dist_df, color="#2E86C1", height=180)

    st.markdown("---")

    # --- 2. 盈虧熱力散佈圖 (Risk-Reward Scatter) ---
    st.subheader("🎯 風險收益定位 (Risk-Reward Mapping)")
    
    scatter_data = []
    for p in players:
        series = player_data_dict[p]
        scatter_data.append({
            "Player": p,
            "期望回報 (Avg)": series.mean(),
            "風險波動 (σ)": series.std()
        })
    df_scatter = pd.DataFrame(scatter_data)

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        st.scatter_chart(df_scatter, x="期望回報 (Avg)", y="風險波動 (σ)", color="Player", size=80, height=300)
    
    with col_s2:
        st.markdown("""
        **💡 散佈圖解析：**
        * **右上角 (Aggressive)**: 高回報、高風險。屬於進攻型，適合在大牌局中博弈。
        * **左上角 (Volatile)**: 低回報、高風險。警訊！代表打法混亂，常出現無謂的巨大損失。
        * **右下角 (Sharpe-Pro)**: 高回報、低風險。這是聖盃位置，代表技術極其穩定。
        """)

    st.markdown("---")

    # --- 3. 水下圖 (Underwater Plot / Drawdown) ---
    st.subheader("🌊 心理壓力與回撤監控 (Underwater Plot)")
    
    underwater_df = pd.DataFrame()
    for p in players:
        equity = player_data_dict[p].cumsum()
        drawdown = equity - equity.cummax() # 計算偏度最高點的跌幅
        underwater_df[p] = drawdown

    st.area_chart(underwater_df, height=250)
    
    
    
    st.markdown("""
    **💡 水下圖解析：**
    * **線條越接近 0**: 代表該玩家正處於歷史巔峰，心理狀態（Confidence）最佳。
    * **深水區 (<-300)**: 代表該玩家正遭遇嚴重連輸。這時對手容易進入 **Tilt (情緒失控)**，是進攻他的好時機。
    * **恢復速度**: 觀察線條回到 0 的坡度。坡度越陡，代表該玩家「回血」能力與抗壓性越強。
    """)

    st.markdown("---")

    # --- 4. SMA(5) 趨勢動能圖 ---
    st.subheader("📈 SMA(5) 趨勢動能")
    trend_cols = st.columns(2)
    for i, p in enumerate(players):
        with trend_cols[i % 2]:
            equity_curve = player_data_dict[p].cumsum()
            df_trend = pd.DataFrame({
                "Equity": equity_curve,
                "SMA(5)": equity_curve.rolling(window=5).mean()
            })
            st.line_chart(df_trend, height=180)
            st.caption(f"{p} 趨勢")
