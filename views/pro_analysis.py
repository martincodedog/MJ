import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計終端</h2>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足：量化模型需要至少 5 場數據以生成有效指標。")
        return

    player_data_dict = {p: pd.to_numeric(df_master[p], errors='coerce').fillna(0) for p in players}

    # --- 1. 損益頻率分布與核心矩 ---
    st.subheader("📊 損益頻率分布與核心矩 (Stats Distribution)")
    bins = [-float('inf'), -500, -300, -100, 0, 100, 300, 500, float('inf')]
    labels = ["<-500", "-300", "-100", "<0", ">0", "+100", "+300", ">500"]

    chart_cols = st.columns(2)
    for i, p in enumerate(players):
        with chart_cols[i % 2]:
            series = player_data_dict[p]
            st.markdown(f"""
                <div style='background:#F8F9F9; padding:10px; border-radius:5px; border-left:4px solid #2E86C1;'>
                    <b style='font-size:14px;'>👤 {p}</b><br>
                    <span style='font-size:11px; color:#566573;'>
                        Mean: <b>{series.mean():.1f}</b> | SD: <b>{series.std():.1f}</b> | Skew: <b>{series.skew():.2f}</b>
                    </span>
                </div>
            """, unsafe_allow_html=True)
            dist_df = pd.cut(series, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
            st.bar_chart(dist_df, color="#2E86C1", height=160)

    st.info("""
    **📝 統計指標說明：**
    * **Mean (期望值)**：長期而言，平均每一場你能贏（或輸）的分數。
    * **SD (標準差)**：數值越高代表打法越激進，損益上下震盪劇烈，對心理素質要求較高。
    * **Skew (偏度)**：衡量獲利分布。**正偏 (>0)** 代表有能力胡大牌或捕捉大波段；**負偏 (<0)** 警告你平時小贏但存在一次「大爆掉」的結構性風險。
    """)
    

    st.divider()

    # --- 2. 滾動夏普比率 ---
    st.subheader("🛡️ 滾動夏普比率 (Rolling Sharpe Ratio)")
    rolling_sharpe_df = pd.DataFrame()
    for p in players:
        series = player_data_dict[p]
        roll_mean = series.rolling(window=5).mean()
        roll_std = series.rolling(window=5).std()
        rolling_sharpe_df[p] = roll_mean / roll_std
    st.line_chart(rolling_sharpe_df.replace([np.inf, -np.inf], np.nan), height=250)

    st.info("""
    **📝 滾動夏普說明：**
    * **意義**：衡量「每單位風險能換到的回報」。它比總分更能體現技巧的純度。
    * **判讀**：數值越高且越平穩，代表你的獲利越依靠「技術」而非「運氣」。若數值劇烈震盪，代表近期的表現極度不穩定。
    """)

    st.divider()

    # --- 3. RSI 手感強度指標 ---
    st.subheader("🔥 RSI 手感強度監控 (Relative Strength Index)")
    rsi_df = pd.DataFrame()
    for p in players:
        series = player_data_dict[p]
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=5).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=5).mean()
        rs = gain / loss
        rsi_df[p] = 100 - (100 / (1 + rs))

    st.line_chart(rsi_df, height=250)
    
    st.info("""
    **📝 RSI 手感說明：**
    * **RSI > 70 (超買/發燙)**：玩家手感極佳或運氣處於頂峰，需注意隨後的均值回歸。
    * **RSI < 30 (超賣/冰冷)**：玩家處於連敗低潮。這時需觀察其是否進入 Tilt (情緒失控) 狀態，是戰術進攻的機會點。
    """)
    

    st.divider()

    # --- 4. 累積資產走勢與 SMA(5) ---
    st.subheader("📈 累積資產走勢與 SMA(5)")
    trend_cols = st.columns(len(players))
    for i, p in enumerate(players):
        with trend_cols[i]:
            equity = player_data_dict[p].cumsum()
            df_trend = pd.DataFrame({"Equity": equity, "SMA5": equity.rolling(window=5).mean()})
            st.line_chart(df_trend, height=150)
            st.caption(f"{p} 累積資產與 5 日均線")

    st.info("""
    **📝 趨勢動能說明：**
    * **Equity (實線)**：你真正的財富累積路徑。
    * **SMA5 (虛線)**：5 場移動平均線。當實線穿過虛線向上時，代表你處於**黃金交叉**，技術與運氣正處於上升趨勢。
    """)
