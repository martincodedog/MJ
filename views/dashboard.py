import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📊 戰績深度分析</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無數據。")
        return

    # --- 1. 最近對局戰績 (加大字體) ---
    st.subheader("🏁 最近對局戰績")
    last_row = df_master.iloc[-1]
    m_cols = st.columns(2)
    for i, p in enumerate(players):
        val = last_row[p]
        color = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with m_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#f8f9fa; padding:15px 10px; border-radius:15px; border-left:8px solid {color}; margin-bottom:12px; box-shadow: 2px 2px 5px rgba(0,0,0,0.03);">
                    <p style="margin:0; font-size:14px; color:#555; font-weight:bold;">{p}</p>
                    <p style="margin:2px 0 0 0; font-size:28px; font-weight:900; color:{color}; line-height:1;">{int(val):+d}</p>
                </div>
            """, unsafe_allow_html=True)
    st.caption(f"📅 紀錄日期：{last_row['Date']}")
    st.divider()

    # --- 2. 累積資產走勢 ---
    st.subheader("📈 累計財富走勢")
    df_trend = df_master.copy()
    df_trend = df_trend.set_index('Date')[players].cumsum()
    st.line_chart(df_trend, height=300)
    st.divider()

    # --- 3. 核心數據統計 ---
    st.subheader("📉 全方位數據摘要")
    stats_dict = {}
    for p in players:
        data = df_master[p]
        stats_dict[p] = {
            "總分": data.sum(),
            "平均": data.mean(),
            "標準差": data.std(),
            "勝率%": (data > 0).sum() / len(data) * 100,
            "波動": data.max() - data.min()
        }
    stats_df = pd.DataFrame(stats_dict).T
    # 表格字體相對固定，但用加闊模式
    st.dataframe(stats_df.style.format(precision=0), use_container_width=True)
    
    with st.expander("ℹ️ 數據計算說明"):
        st.markdown("基於 Master Record 每日總計：波動區間 (Max-Min)、標準差 (穩定度)、勝率 (贏錢天數%)。")
    st.divider()

    # --- 4. 🔮 下局風向預測 (特大字體卡片) ---
    st.subheader("🔮 下局風向預測")
    predict_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        avg = data.mean()
        std = data.std() if not pd.isna(data.std()) else 0
        recent_trend = data.tail(3).mean()
        
        ev = (avg * 0.7) + (recent_trend * 0.3)
        lower_bound = ev - std
        upper_bound = ev + std
        
        with predict_cols[i % 2]:
            color = "#1e8e3e" if ev > 0 else "#d93025"
            st.markdown(f"""
                <div style="background-color:#ffffff; border:1px solid #eee; padding:15px; border-radius:18px; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); text-align:center;">
                    <p style="margin:0; font-size:16px; font-weight:bold; color:#333;">{p}</p>
                    <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
                    <p style="margin:0; font-size:12px; color:#888; text-transform:uppercase;">Expected Value</p>
                    <p style="margin:2px 0; font-size:32px; font-weight:900; color:{color};">{int(ev):+d}</p>
                    <div style="background-color:#f0f2f6; border-radius:10px; padding:5px; margin-top:10px;">
                        <p style="margin:0; font-size:11px; color:#666;">預測落點</p>
                        <p style="margin:0; font-size:15px; font-weight:bold; color:#333;">{int(lower_bound)} ~ {int(upper_bound)}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- 5. 邏輯說明 ---
    with st.expander("🧠 預測邏輯與期望值說明"):
        st.markdown("""
        1. **期望值 (EV)**: 結合 70% 歷史平均 + 30% 近期走勢。
        2. **預測區間**: 根據**常態分佈**，約 68% 機率落入此範圍。
        """)
