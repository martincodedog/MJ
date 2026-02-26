import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>📊 雀壇全方位量化數據儀表板</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("查無數據，請先輸入對局紀錄。")
        return

    # --- 1. 個人化動態指標卡 (KPI Metrics Cards) ---
    st.subheader("🎯 即時戰力監控與近期走勢 (Real-time Form)")
    
    for p in players:
        # 數據提取
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        current_total = series.sum()
        last_val = series.iloc[-1]
        
        # 近 5 場表現紀錄 (Form Guide: WWLLW)
        last_5 = series.tail(5).tolist()
        form_str = "".join(["<span style='color:#28B463;font-weight:bold;'>W</span>" if x > 0 else 
                            "<span style='color:#E74C3C;font-weight:bold;'>L</span>" if x < 0 else 
                            "<span style='color:#BDC3C7;font-weight:bold;'>D</span>" for x in last_5])
        
        # 動量計算 (Momentum)
        short_ma = series.tail(3).mean()
        long_ma = series.mean()
        momentum_idx = short_ma - long_ma
        
        # 下場預測 (Next Game Expected)
        expected_next = long_ma + (momentum_idx * 0.3)

        # UI 排版
        with st.container():
            # 標題與近期表現 (Last 5 Games)
            st.markdown(f"#### 👤 {p} <span style='font-size:14px; margin-left:15px; background:#F4F6F7; padding:2px 8px; border-radius:4px;'>近期趨勢: {form_str}</span>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Current Score", f"{int(current_total)}", delta=f"{int(series.mean())} (Avg)")
            with c2:
                # 顯示上一場相較於前一場的增減
                diff = int(last_val - series.iloc[-2]) if len(series)>1 else 0
                st.metric("Last Game", f"{int(last_val)}", delta=f"{diff:+} pts")
            with c3:
                st.metric("Next Game Exp.", f"{expected_next:+.1f}", help="基於近期動能與歷史期望值的加權預測")
            with c4:
                m_label = "🔥 強勢" if momentum_idx > 10 else "🧊 轉冷" if momentum_idx < -10 else "⚖️ 平穩"
                st.metric("Momentum", m_label, delta=f"{momentum_idx:+.1f}")
            st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. 全方位數據摘要表格 (轉置矩陣) ---
    st.divider()
    st.subheader("📋 全方位量化數據矩陣 (Indicators Matrix)")
    
    summary_data = {}
    min_periods = 5 
    
    for p in players:
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        price_series = series.cumsum()
        wins = series[series > 0]
        losses = series[series < 0]
        
        # 技術指標
        gain = (series.where(series > 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        loss = (-series.where(series < 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # 財務指標
        win_rate = (len(wins) / len(series)) * 100 if len(series) > 0 else 0
        running_max = price_series.cummax()
        mdd = (price_series - running_max).min()
        pl_ratio = (wins.mean() / abs(losses.mean())) if not losses.empty and losses.mean() != 0 else 0
        sharpe = (series.mean() / series.std()) if series.std() > 0 else 0
        
        summary_data[p] = {
            "RSI 動能": f"{rsi:.1f}",
            "勝率 %": f"{win_rate:.1f}%",
            "最大回撤 MDD": f"{mdd:.0f}",
            "盈虧比 P/L": f"{pl_ratio:.2f}",
            "夏普比率 Sharpe": f"{sharpe:.2f}",
            "波動率 σ": f"{series.std():.1f}"
        }

    st.table(pd.DataFrame(summary_data))

    # --- 3. 資本曲線圖表 ---
    st.subheader("📈 歷史資本累積曲線 (Equity Curve)")
    df_cumulative = df_master[players].cumsum()
    # 確保日期索引正確
    if 'Date' in df_master.columns:
        df_cumulative.index = pd.to_datetime(df_master['Date'])
    st.line_chart(df_cumulative)
