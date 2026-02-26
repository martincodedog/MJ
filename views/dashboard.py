import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📊 戰績深度分析</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無數據，請先到快速計分錄入紀錄。")
        return

    # --- 1. 最近對局戰績 (Last Match Day) ---
    st.subheader("🏁 最近對局戰績")
    last_row = df_master.iloc[-1]
    m_cols = st.columns(2)
    for i, p in enumerate(players):
        val = last_row[p]
        color = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with m_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#f8f9fa; padding:12px 10px; border-radius:12px; border-left:6px solid {color}; margin-bottom:10px;">
                    <p style="margin:0; font-size:13px; color:#666; font-weight:bold;">{p}</p>
                    <p style="margin:2px 0 0 0; font-size:22px; font-weight:900; color:{color};">{int(val):+d}</p>
                </div>
            """, unsafe_allow_html=True)
    st.caption(f"📅 紀錄日期：{last_row['Date']}")
    st.divider()

    # --- 2. 累積資產走勢 ---
    st.subheader("📈 累計財富走勢")
    df_trend = df_master.set_index('Date')[players].cumsum()
    st.line_chart(df_trend, height=300)
    st.divider()

    # --- 3. 核心數據統計 (加強版) ---
    st.subheader("📉 全方位數據摘要")
    
    # 計算進階統計指標
    summary_dict = {
        "總累積積分": df_master[players].sum(),
        "平均單日表現": df_master[players].mean(),
        "單日最高紀錄": df_master[players].max(),
        "單日最低紀錄": df_master[players].min(),
        "波動區間 (Max-Min)": df_master[players].max() - df_master[players].min(),
        "標準差 (穩定度)": df_master[players].std(),
        "勝率 (贏錢天數%)": (df_master[players] > 0).sum() / len(df_master) * 100,
        "連勝/連敗次數": None # 邏輯較複雜可後補，目前先放核心指標
    }
    
    # 建立表格並美化
    stats_df = pd.DataFrame(summary_dict).T
    st.dataframe(
        stats_df.style.format(precision=0, na_rep='-'),
        use_container_width=True
    )
    
    with st.expander("ℹ️ 如何解讀這些指標？"):
        st.markdown("""
        * **標準差 (Standard Deviation)**: 數值越小，代表表現越穩定；數值越大，代表該玩家是「神鬼莫測」的爆發型選手。
        * **波動區間**: 反映該玩家單日戰績的最極端範圍。
        * **平均單日表現**: 長期而言，該玩家每次開枱平均會帶走（或留下）多少錢。
        """)

    st.divider()

    # --- 4. 下局預測 (Next Game Predict) ---
    st.subheader("🔮 下局風向預測")
    
    # 簡單預測邏輯：結合近期勢頭 (Momentum) 同 均值回歸 (Mean Reversion)
    prediction_results = []
    
    for p in players:
        recent_scores = df_master[p].tail(3).tolist() # 攞最近三場
        avg_score = df_master[p].mean()
        last_score = recent_scores[-1]
        
        # 邏輯 A: 近期勢頭 (Momentum) - 最近三場都係正/負
        momentum = "🔥 氣勢如虹" if all(x > 0 for x in recent_scores) else "❄️ 運勢低迷" if all(x < 0 for x in recent_scores) else "⚖️ 狀態平穩"
        
        # 邏輯 B: 均值回歸 (Mean Reversion) - 輸得多會贏返
        if last_score < -200: 
            advice = "反彈機會大"
        elif last_score > 200:
            advice = "居安思危"
        else:
            advice = "隨緣發揮"
            
        prediction_results.append({"玩家": p, "當前勢頭": momentum, "分析建議": advice})

    # 顯示預測卡片
    p_cols = st.columns(2)
    for i, res in enumerate(prediction_results):
        with p_cols[i % 2]:
            st.info(f"**{res['玩家']}**\n\n{res['當前勢頭']}\n\n💡 {res['分析建議']}")

    with st.expander("🧠 預測邏輯說明"):
        st.markdown("""
        預測結果由以下簡易演算法得出：
        1. **近期勢頭 (Momentum)**: 觀察最近 3 場的表現。若連續 3 場獲利，判定為「氣勢如虹」；連續 3 場虧損，則為「運勢低迷」。
        2. **均值回歸 (Mean Reversion)**: 根據「數極必反」原則。若上局虧損極大，則系統判定下局「反彈」機率上升；反之，若上局大勝，則建議「居安思危」。
        
        *注意：麻雀始終涉及隨機性與技術，預測僅供娛樂參考。*
        """)
