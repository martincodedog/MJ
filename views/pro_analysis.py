import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h3 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計 (終極版)</h3>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足，至少需要 5 場紀錄以計算 RSI 與滾動指標。")
        return

    player_data_dict = {p: pd.to_numeric(df_master[p], errors='coerce').fillna(0) for p in players}

    # --- 1. 高密度頻率分佈矩陣 (含統計特徵) ---
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

    st.markdown("---")

    # --- 2. 滾動夏普比率 (Rolling Sharpe Ratio) ---
    st.subheader("🛡️ 滾動夏普比率 (Rolling Sharpe - Window: 5)")
    rolling_sharpe_df = pd.DataFrame()
    for p in players:
        series = player_data_dict[p]
        roll_mean = series.rolling(window=5).mean()
        roll_std = series.rolling(window=5).std()
        rolling_sharpe_df[p] = roll_mean / roll_std
    st.line_chart(rolling_sharpe_df.replace([np.inf, -np.inf], np.nan), height=250)

    st.markdown("---")

    # --- 3. [新增] RSI 手感強度指標 (Relative Strength Index) ---
    st.subheader("🔥 RSI 手感強度監控 (Window: 5)")
    
    rsi_df = pd.DataFrame()
    for p in players:
        series = player_data_dict[p]
        # 計算漲跌幅
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=5).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=5).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_df[p] = rsi

    # 繪製 RSI 線圖
    st.line_chart(rsi_df, height=250)
    
    

    with st.expander("💡 如何解讀 RSI 手感指標？"):
        st.markdown("""
        * **RSI > 70 (Overbought / Hot)**: 該玩家處於連勝的高點（手感發燙）。在金融中這叫超買，在雀壇這代表運氣成分可能已達峰值，下一場出現回調（輸錢）的機率增加。
        * **RSI < 30 (Oversold / Cold)**: 該玩家處於連敗低谷（手感冰冷）。這是一個危險訊號，若伴隨 Skewness 為負，代表該玩家可能已經「上頭 (Tilt)」。
        * **中軸 50**: 代表獲利與虧損處於平衡狀態，技巧發揮正常。
        """)

    st.markdown("---")

    # --- 4. 趨勢動能 SMA(5) ---
    st.subheader("📈 累積資產走勢與 SMA(5)")
    trend_cols = st.columns(len(players))
    for i, p in enumerate(players):
        with trend_cols[i]:
            equity = player_data_dict[p].cumsum()
            df_trend = pd.DataFrame({"Equity": equity, "SMA5": equity.rolling(window=5).mean()})
            st.line_chart(df_trend, height=150)
            st.caption(f"{p} 累積資產")
