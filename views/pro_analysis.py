import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h3 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計 (精簡版)</h3>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足，無法計算 SMA(5) 與相關量化指標。")
        return

    # --- 1. 核心指標表 ---
    quant_metrics = []
    player_data_dict = {}
    for p in players:
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        player_data_dict[p] = series
        quant_metrics.append({
            "Player": p,
            "Mean": series.mean(),
            "σ": series.std(),
            "Sharpe": (series.mean() / series.std()) if series.std() > 0 else 0,
            "MDD": (series.cumsum() - series.cumsum().cummax()).min()
        })
    df_quant = pd.DataFrame(quant_metrics).set_index("Player")
    st.dataframe(df_quant.style.format(precision=1).background_gradient(cmap="RdYlGn", subset=["Sharpe"]), use_container_width=True)

    with st.expander("🔬 指標速查"):
        st.markdown("""
        * **Sharpe**: 越高代表穩定性越好。
        * **SMA(5)**: 近 5 場平均線，用於過濾隨機波動，觀察真實趨勢。
        * **分佈圖**: 觀察長條是否集中在中間（穩健）或兩端（賭性）。
        """)

    # --- 2. 小型化損益分佈圖 ---
    st.markdown("---")
    st.subheader("📊 損益密度矩陣 (-500 ~ +500)")
    bins = [-float('inf'), -500, -300, -100, 0, 100, 300, 500, float('inf')]
    labels = ["<-500", "-300", "-100", "<0", ">0", "+100", "+300", ">500"]

    chart_cols = st.columns(2)
    for i, p in enumerate(players):
        with chart_cols[i % 2]:
            st.markdown(f"<p style='margin-bottom:-10px; font-size:14px; font-weight:bold; color:#2E86C1;'>● {p} 分佈</p>", unsafe_allow_html=True)
            data = player_data_dict[p]
            dist_df = pd.cut(data, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
            st.bar_chart(dist_df, color="#2E86C1", height=180)

    # --- 3. SMA(5) 趨勢動能圖 (Trend Momentum) ---
    st.markdown("---")
    st.subheader("📈 累計資產與 SMA(5) 動能趨勢")
    
    # 將玩家分成兩組顯示，節省垂直空間
    trend_cols = st.columns(2)
    for i, p in enumerate(players):
        with trend_cols[i % 2]:
            st.markdown(f"<p style='margin-bottom:5px; font-size:14px; font-weight:bold; color:#1B4F72;'>{p} 趨勢線</p>", unsafe_allow_html=True)
            
            # 計算累計得分與 SMA(5)
            equity_curve = player_data_dict[p].cumsum()
            sma_5 = equity_curve.rolling(window=5).mean()
            
            # 建立繪圖用的 DataFrame
            df_trend = pd.DataFrame({
                "Equity (實時資產)": equity_curve,
                "SMA(5) (動能均線)": sma_5
            })
            
            # 使用 st.line_chart 渲染
            st.line_chart(df_trend, height=200)
