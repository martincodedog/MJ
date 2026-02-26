import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h3 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險量化審計 (精簡版)</h3>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足。")
        return

    # --- 1. 核心指標表 (保持現狀，因為它最節省空間) ---
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

    # --- 2. 小型化損益分佈圖 (Small Charts) ---
    st.markdown("---")
    st.subheader("📊 損益密度矩陣 (-500 ~ +500)")
    
    # 縮短標籤以節省空間
    bins = [-float('inf'), -500, -300, -100, 0, 100, 300, 500, float('inf')]
    labels = ["<-500", "-300", "-100", "<0", ">0", "+100", "+300", ">500"]

    # 使用 2 欄佈局縮小圖表尺寸
    chart_cols = st.columns(2)
    for i, p in enumerate(players):
        with chart_cols[i % 2]:
            st.markdown(f"<p style='margin-bottom:-10px; font-size:14px; font-weight:bold; color:#2E86C1;'>● {p}</p>", unsafe_allow_html=True)
            
            data = player_data_dict[p]
            dist_df = pd.cut(data, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
            
            # 渲染小型圖表
            st.bar_chart(dist_df, color="#2E86C1", height=180) 

    # --- 3. 策略簡評 (緊湊排列) ---
    st.markdown("---")
    prof_cols = st.columns(len(players))
    for i, p in enumerate(players):
        s_ratio = df_quant.loc[p, "Sharpe"]
        mdd = df_quant.loc[p, "MDD"]
        
        if s_ratio > 0.8: status, color = "穩健 Alpha", "#28B463"
        elif mdd < -400: status, color = "高壓風險", "#E74C3C"
        else: status, color = "中性 Beta", "#5D6D7E"
        
        with prof_cols[i]:
            st.markdown(f"""
                <div style="border-top: 3px solid {color}; background:#F8F9F9; padding:10px; border-radius:0 0 5px 5px; text-align:center;">
                    <b style="font-size:12px;">{p}</b><br>
                    <span style="font-size:11px; color:{color};">{status}</span>
                </div>
            """, unsafe_allow_html=True)

    # 統計手冊 (摺疊以省空間)
    with st.expander("🔬 指標速查"):
        st.markdown("""
        * **Sharpe**: 越高代表穩定性越好。
        * **MDD**: 最大虧損紀錄。
        * **分佈圖**: 觀察長條是否集中在中間（穩健）或兩端（賭性）。
        """)
