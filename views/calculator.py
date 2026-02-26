import streamlit as st
import pandas as pd

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📊 戰績分析中心</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無數據，請先到快速計分錄入紀錄。")
        return

    # --- 1. 最近對局戰績 (Last Match Day) ---
    st.subheader("🏁 最近對局戰績")
    last_row = df_master.iloc[-1]
    last_date = last_row['Date']
    
    # 2x2 佈局顯示最近分數，字體調大方便 iPhone 閱讀
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
    st.caption(f"📅 最近紀錄日期：{last_date}")
    st.divider()

    # --- 2. 累積資產走勢 (原生 Line Chart) ---
    st.subheader("📈 累計財富走勢")
    
    # 準備累計數據
    df_trend = df_master.copy()
    # 確保 Date 是 index 方便圖表顯示日期軸
    df_trend = df_trend.set_index('Date')[players].cumsum()
    
    # 使用 Streamlit 原生圖表，自動適應手機闊度
    st.line_chart(df_trend, height=300)
    st.divider()

    # --- 3. 數據統計摘要 (Summary Stats) ---
    st.subheader("📉 核心數據統計")
    
    # 計算各項指標
    stats = pd.DataFrame({
        "總分": df_master[players].sum(),
        "平均": df_master[players].mean(),
        "最高": df_master[players].max(),
        "最低": df_master[players].min(),
        "波動區間": df_master[players].max() - df_master[players].min(),
        "勝率 (%)": (df_master[players] > 0).sum() / len(df_master) * 100
    }).T
    
    # 使用 dataframe 顯示表格，關閉 index 以節省空間
    st.dataframe(
        stats.style.format("{:.0f}"),
        use_container_width=True
    )

    # --- 4. 數據計算說明 (Markdown Note) ---
    st.write("")
    with st.expander("ℹ️ 數據計算說明 (Summary Stats Logic)"):
        st.markdown(f"""
        本系統之統計指標均基於 **Master Record** 內之每日總計數據：
        
        * **波動區間 (Volatility Range)**: 
            * `計算公式：最高分 (Max) - 最低分 (Min)`
            * **意義**：反映表現的穩定性。區間越大，代表該玩家戰績起伏較大（俗稱「大進大出」）。
        * **平均表現 (Average)**: 
            * `計算公式：總分 / 總對局天數`
            * **意義**：反映長期戰力的平均水位。
        * **勝率 (Win Rate %)**: 
            * `計算公式：(贏錢天數 / 總對局天數) * 100%`
            * **意義**：反映該玩家穩定獲利（正分收場）的機率。
        * **最高 / 最低**: 
            * 記錄該玩家單日戰績的巅峰與低谷。
        
        ---
        *備註：波動區間與打法風向有關，數值僅供參考，不代表絕對技術水準。*
        """)
