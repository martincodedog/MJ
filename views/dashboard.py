import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>📊 雀壇全方位量化數據儀表板</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("查無數據，請先輸入對局紀錄。")
        return

    # --- 1. 個人化動態指標卡 (KPI Metrics Cards) ---
    st.subheader("🎯 即時戰力監控 (Real-time Metrics)")
    
    for p in players:
        # 數據提取
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        current_total = series.sum()
        last_val = series.iloc[-1]
        
        # 動量計算 (Momentum): 近三場平均 vs 歷史平均
        short_ma = series.tail(3).mean()
        long_ma = series.mean()
        momentum_idx = short_ma - long_ma
        
        # 下場預測 (Next Game Expected): 基於期望值與動量權重的簡單線性預測
        # 公式：歷史平均 + (動量權重 * 0.3)
        expected_next = long_ma + (momentum_idx * 0.3)

        # UI 排版
        with st.container():
            st.markdown(f"#### 👤 {p}")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.metric("Current Score", f"{int(current_total)}", delta=f"{int(series.mean())} (Avg)")
            with c2:
                st.metric("Last Game", f"{int(last_val)}", delta=f"{int(last_val - series.iloc[-2]) if len(series)>1 else 0}")
            with c3:
                st.metric("Next Game Exp.", f"{expected_next:+.1f}", help="基於近期動能與歷史期望值的加權預測")
            with c4:
                m_label = "🔥 強勢" if momentum_idx > 10 else "🧊 轉冷" if momentum_idx < -10 else "⚖️ 平穩"
                st.metric("Momentum", m_label, delta=f"{momentum_idx:+.1f}")
            st.markdown("---")

    # --- 2. 全方位數據摘要表格 (轉置矩陣) ---
    st.subheader("📋 全方位量化數據矩陣 (Indicators Matrix)")
    
    summary_data = {}
    min_periods = 5 
    
    for p in players:
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        price_series = series.cumsum()
        wins = series[series > 0]
        losses = series[series < 0]
        
        # 技術指標運算
        delta = series
        gain = (delta.where(delta > 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        ema12 = price_series.ewm(span=12, adjust=False).mean()
        ema26 = price_series.ewm(span=26, adjust=False).mean()
        macd = (ema12 - ema26).iloc[-1]

        # 財務與精算指標
        win_rate = (len(wins) / len(series)) * 100 if len(series) > 0 else 0
        running_max = price_series.cummax()
        mdd = (price_series - running_max).min()
        pl_ratio = (wins.mean() / abs(losses.mean())) if not losses.empty and losses.mean() != 0 else 0
        sharpe = (series.mean() / series.std()) if series.std() > 0 else 0
        
        summary_data[p] = {
            "RSI 動能": f"{rsi:.1f}",
            "MACD 動量": f"{macd:.1f}",
            "勝率 %": f"{win_rate:.1f}%",
            "最大回撤 MDD": f"{mdd:.0f}",
            "盈虧比 P/L": f"{pl_ratio:.2f}",
            "夏普比率 Sharpe": f"{sharpe:.2f}",
            "波動率 σ": f"{series.std():.1f}"
        }

    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)

    # --- 3. 資本曲線圖表 ---
    st.subheader("📈 歷史資本累積曲線 (Equity Curve)")
    df_cumulative = df_master[players].cumsum()
    df_cumulative.index = pd.to_datetime(df_master['Date'])
    st.line_chart(df_cumulative)

    with st.expander("📚 指標定義與預測邏輯"):
        st.markdown("""
        * **Next Game Expected**: 利用資產獲利平穩性與近期動能進行建模，預測下一場對局的收益中位數。
        * **Momentum (動量)**: 比較短期（3場）與長期（總體）平均值。若短期表現優於長期，則視為進入「🔥 強勢」上升軌道。
        * **Sharpe Ratio**: 判斷該玩家獲利是源於純粹手風 (Volatility) 還是穩定戰術。
        """)
