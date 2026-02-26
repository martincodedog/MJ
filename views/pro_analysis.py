import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h3 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計 (精煉視覺版)</h3>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足，無法生成進階分析。")
        return

    player_data_dict = {p: pd.to_numeric(df_master[p], errors='coerce').fillna(0) for p in players}

    # --- 1. 損益密度矩陣 ---
    st.subheader("📊 損益密度分布 (-500 ~ +500)")
    bins = [-float('inf'), -500, -300, -100, 0, 100, 300, 500, float('inf')]
    labels = ["<-500", "-300", "-100", "<0", ">0", "+100", "+300", ">500"]

    chart_cols = st.columns(2)
    for i, p in enumerate(players):
        with chart_cols[i % 2]:
            st.markdown(f"<p style='margin-bottom:-10px; font-size:13px; font-weight:bold; color:#2E86C1;'>● {p} 分佈</p>", unsafe_allow_html=True)
            dist_df = pd.cut(player_data_dict[p], bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
            st.bar_chart(dist_df, color="#2E86C1", height=160)

    st.markdown("---")

    # --- 2. 風險收益定位散佈圖 ---
    st.subheader("🎯 風險收益定位 (Risk-Reward Mapping)")
    scatter_data = [{"Player": p, "Avg": player_data_dict[p].mean(), "Sigma": player_data_dict[p].std()} for p in players]
    st.scatter_chart(pd.DataFrame(scatter_data), x="Avg", y="Sigma", color="Player", size=100, height=300)
    
    with st.expander("💡 散佈圖如何輔助決策？"):
        st.markdown("觀察玩家在座標軸的位置。靠近**右下角**代表該玩家具備穩定的「收割能力」；靠近**上方**則代表其情緒波動大，容易出現極端胡牌或放銃。")

    st.markdown("---")

    # --- 3. [新增] 獲利韌性對比 (Profit Resilience - Bar Chart) ---
    # 相比 area_chart，長條圖更能清晰看出誰的抗壓性更好
    st.subheader("🛡️ 獲利韌性與最大損失對比")
    
    resilience_data = []
    for p in players:
        series = player_data_dict[p]
        equity = series.cumsum()
        max_drawdown = (equity - equity.cummax()).min()
        resilience_data.append({
            "Player": p,
            "最大回撤 (MDD)": max_drawdown,
            "平均單場損益": series.mean()
        })
    df_res = pd.DataFrame(resilience_data).set_index("Player")
    
    st.bar_chart(df_res, height=250)
    
    st.markdown("""
    **💡 韌性圖表解析：**
    * **負向柱狀越長**: 代表該玩家的「心理防線」越容易崩潰（曾有過巨大虧損）。
    * **對比分析**: 若平均損益為正，但 MDD 極大，代表該玩家是「富貴險中求」，資產極不安全。
    """)

    st.markdown("---")

    # --- 4. 趨勢動能 SMA(5) (改為單人多列顯示，增加清晰度) ---
    st.subheader("📈 SMA(5) 趨勢動能對比")
    trend_cols = st.columns(len(players))
    for i, p in enumerate(players):
        with trend_cols[i]:
            st.markdown(f"<p style='text-align:center; font-size:12px; font-weight:bold;'>{p}</p>", unsafe_allow_html=True)
            equity_curve = player_data_dict[p].cumsum()
            df_trend = pd.DataFrame({
                "Eq": equity_curve,
                "SMA5": equity_curve.rolling(window=5).mean()
            })
            # 移除 area_chart，改用純線圖
            st.line_chart(df_trend, height=150, use_container_width=True)

    with st.expander("📝 統計學手冊"):
        st.markdown("""
        * **SMA(5)**: 實線 (Eq) 在虛線 (SMA5) 之上時，代表該玩家正處於「技術上升期」。
        * **Sigma (σ)**: 反映打法的激進程度，數值越高代表越容易出現「大輸大贏」。
        """)
