import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📊 戰績深度分析中心</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無數據，請先到快速計分錄入紀錄。")
        return

    # --- 1. 最近對局戰績 (Last Match Day Points) ---
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

    # --- 2. 累積資產走勢 (Cumulative Trend) ---
    st.subheader("📈 累計財富走勢")
    df_trend = df_master.copy()
    df_trend = df_trend.set_index('Date')[players].cumsum()
    st.line_chart(df_trend, height=300)
    st.divider()

    # --- 3. 核心數據統計 (All Summary Stats) ---
    st.subheader("📉 全方位數據摘要")
    
    stats_dict = {}
    for p in players:
        data = df_master[p]
        stats_dict[p] = {
            "總累積積分": data.sum(),
            "平均單日表現": data.mean(),
            "單日最高紀錄": data.max(),
            "單日最低紀錄": data.min(),
            "波動區間 (Range)": data.max() - data.min(),
            "標準差 (穩定度)": data.std(),
            "勝率 (%)": (data > 0).sum() / len(data) * 100
        }
    
    stats_df = pd.DataFrame(stats_dict).T
    st.dataframe(stats_df.style.format(precision=0), use_container_width=True)
    
    with st.expander("ℹ️ 數據計算說明 (Summary Stats Logic)"):
        st.markdown("""
        本系統之統計指標均基於 **Master Record** 內之每日總計數據：
        
        * **波動區間 (Volatility Range)**: 
            * `計算公式：最高分 (Max) - 最低分 (Min)`
            * **意義**：反映表現的穩定性。區間越大，代表該玩家戰績起伏較大（俗稱「大進大出」）。
        * **標準差 (Standard Deviation)**: 
            * 反映分數偏離平均值的程度。數值越小，代表表現越穩定；數值越大，代表該玩家是爆發型選手。
        * **勝率 (Win Rate %)**: 
            * `計算公式：(贏錢天數 / 總對局天數) * 100%`
            * **意義**：反映該玩家穩定獲利（正分收場）的機率。
        """)
    st.divider()

    # --- 4. 🔮 下局風向預測 (EV & Predicted Range) ---
    st.subheader("🔮 下局風向預測")
    
    predict_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        avg = data.mean()
        std = data.std() if not pd.isna(data.std()) else 0
        recent_trend = data.tail(3).mean() # 最近三場平均
        
        # 期望值 (EV): 70% 歷史平均 + 30% 近期趨勢
        ev = (avg * 0.7) + (recent_trend * 0.3)
        
        # 預測區間: EV +/- 1個標準差 (約 68% 置信區間)
        lower_bound = ev - std
        upper_bound = ev + std
        
        with predict_cols[i % 2]:
            color = "#1e8e3e" if ev > 0 else "#d93025"
            st.markdown(f"""
                <div style="background-color:#ffffff; border:1px solid #ddd; padding:12px; border-radius:15px; margin-bottom:15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <p style="margin:0; font-size:14px; font-weight:bold; color:#333;">{p}</p>
                    <hr style="margin:8px 0;">
                    <p style="margin:0; font-size:11px; color:#666;">下局期望值 (EV)</p>
                    <p style="margin:0; font-size:22px; font-weight:900; color:{color};">{int(ev):+d}</p>
                    <p style="margin:10px 0 0 0; font-size:11px; color:#666;">預測落點區間</p>
                    <p style="margin:0; font-size:13px; font-weight:bold; color:#444;">
                        {int(lower_bound)} ~ {int(upper_bound)}
                    </p>
                </div>
            """, unsafe_allow_html=True)

    # --- 5. 預測邏輯說明 ---
    with st.expander("🧠 預測邏輯與期望值說明"):
        st.markdown(f"""
        ### 如何理解預測數據？
        
        1. **期望值 (Expected Value, EV)**:
           * 公式：$EV = (\mu \times 0.7) + (M_{{recent}} \times 0.3)$
           * 我們結合了**長期平均表現 ($\mu$)** 與**近期勢頭 ($M_{{recent}}$)**。
           * 若 $EV > 0$，代表數據面支持你下局獲利。

        2. **預測區間 (Predicted Range)**:
           * 根據統計學的**常態分佈 (Normal Distribution)** 原則，約有 **68%** 的對局分數會落在平均值正負一個**標準差 ($\sigma$)** 的範圍內。
           * 區間愈闊，代表該玩家打法愈激進，勝負手較大。
        """)
        
        st.write("---")
        st.markdown("##### [常態分佈參考圖]")
        
        st.caption("註：數據僅供娛樂參考，打牌運氣與心態是無法數據化的。")
