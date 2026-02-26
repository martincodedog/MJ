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

    st.info("**Mean**: 期望值 | **SD**: 激進程度 | **Skew**: 正偏代表具大贏潛力，負偏代表潛藏大賠風險。")
    

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
    st.info("衡量「技術純度」。數值越高且越平穩，代表獲利越依靠實力而非運氣。")

    st.divider()

    # --- 3. [分拆] RSI 手感強度指標 ---
    st.subheader("🔥 RSI 手感強度監控 (Relative Strength Index)")
    
    rsi_cols = st.columns(2) # 採用 2x2 佈局顯示 4 位玩家
    for i, p in enumerate(players):
        with rsi_cols[i % 2]:
            series = player_data_dict[p]
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=5).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=5).mean()
            rs = gain / loss
            rsi_val = 100 - (100 / (1 + rs))
            
            st.markdown(f"<p style='text-align:center; font-size:12px; font-weight:bold; color:#E74C3C;'>{p} RSI 手感</p>", unsafe_allow_html=True)
            st.line_chart(rsi_val, height=150)

    
    st.info("**RSI > 70**: 手感發燙，需防回調 | **RSI < 30**: 手感冰冷，觀察是否進入情緒失控 (Tilt)。")

    st.divider()

    # --- 4. 累積資產走勢與 SMA(5) ---
    st.subheader("📈 累積資產走勢與 SMA(5)")
    trend_cols = st.columns(2)
    for i, p in enumerate(players):
        with trend_cols[i % 2]:
            equity = player_data_dict[p].cumsum()
            df_trend = pd.DataFrame({"Equity": equity, "SMA5": equity.rolling(window=5).mean()})
            st.markdown(f"<p style='text-align:center; font-size:12px; font-weight:bold;'>{p} 趨勢動能</p>", unsafe_allow_html=True)
            st.line_chart(df_trend, height=180)

    st.info("**Equity (實線)**: 財富路徑 | **SMA5 (虛線)**: 實力趨勢。實線高於虛線代表處於技術上升期。")
