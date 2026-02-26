import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>📊 雀壇全方位量化數據儀表板</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("查無數據，請先輸入對局紀錄。")
        return

    # --- 1. 全方位數據摘要 (指標為行，玩家為列) ---
    st.subheader("📋 全方位量化數據摘要 (Indicators Matrix)")
    
    summary_data = {}
    min_periods = 5 
    
    for p in players:
        # 基礎數據與轉換
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        price_series = series.cumsum()
        wins = series[series > 0]
        losses = series[series < 0]
        
        # --- A. 原有技術指標 ---
        # RSI
        delta = series
        gain = (delta.where(delta > 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=min_periods, min_periods=1).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        ema12 = price_series.ewm(span=12, adjust=False).mean()
        ema26 = price_series.ewm(span=26, adjust=False).mean()
        macd = (ema12 - ema26).iloc[-1]

        # --- B. 新增 5 個專業計量指標 ---
        # 1. 勝率 (Win Rate %): 正分局數 / 總局數
        win_rate = (len(wins) / len(series)) * 100 if len(series) > 0 else 0
        
        # 2. 最大回撤 (Max Drawdown): 資本從峰值跌落的最慘幅度
        running_max = price_series.cummax()
        drawdown = price_series - running_max
        mdd = drawdown.min()
        
        # 3. 盈虧比 (Profit/Loss Ratio): 平均贏分 / 平均輸分
        avg_win = wins.mean() if not wins.empty else 0
        avg_loss = abs(losses.mean()) if not losses.empty else 1
        pl_ratio = avg_win / avg_loss
        
        # 4. 夏普比率 (Sharpe Ratio): 單位風險下的超額回報
        sigma = series.std()
        avg_ret = series.mean()
        sharpe = (avg_ret / sigma) if sigma > 0 else 0
        
        # 5. 凱利準則 (Kelly Criterion %): 建議投入的倉位比例（反映獲利優勢）
        # 公式: K% = W - [(1-W) / R], W=勝率, R=盈虧比
        w_p = win_rate / 100
        kelly = (w_p - ((1 - w_p) / pl_ratio)) * 100 if pl_ratio > 0 else 0
        
        # 彙整所有指標
        summary_data[p] = {
            "RSI 動能趨勢": f"{rsi:.1f}",
            "MACD 動量": f"{macd:.1f}",
            "勝率 (Win Rate)": f"{win_rate:.1f}%",
            "最大回撤 (MDD)": f"{mdd:.0f}",
            "盈虧比 (P/L Ratio)": f"{pl_ratio:.2f}",
            "夏普比率 (Sharpe)": f"{sharpe:.2f}",
            "波動率 (Sigma σ)": f"{sigma:.1f}",
            "凱利建議倉位 %": f"{max(0, kelly):.1f}%"
        }

    # 轉置 DataFrame：指標變為行，玩家變為列
    df_summary = pd.DataFrame(summary_data)
    
    # 顯示全方位摘要表
    st.table(df_summary)

    # --- 2. 補充視覺化圖表 ---
    st.markdown("---")
    st.subheader("📈 策略風險與回報分析")
    
    # 展示盈虧比與勝率的對比分佈 (Image Placeholder for concept)
    # 

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("💰 累積資本曲線")
        df_cumulative = df_master[players].cumsum()
        st.line_chart(df_cumulative)
        
    with col_chart2:
        st.write("📊 波動率 (σ) 與 盈虧比 (R) 對比")
        # 簡單展示波動數據
        vol_data = pd.DataFrame({
            "玩家": players,
            "波動率": [float(summary_data[p]["波動率 (Sigma σ)"]) for p in players]
        }).set_index("玩家")
        st.bar_chart(vol_data)

    # --- 3. 指標小科普 ---
    with st.expander("📚 新增指標財經解讀"):
        st.markdown("""
        * **最大回撤 (MDD)**: 衡量該玩家最長「連輸期」的資本損失程度。
        * **盈虧比 (P/L Ratio)**: 反映「贏大錢、輸小錢」的能力。比例 > 1 代表贏面期望值高。
        * **夏普比率 (Sharpe)**: 核心指標。數值越高，代表獲利愈不依賴運氣，而是穩定的技術輸出。
        * **凱利準則 (Kelly Criterion)**: 計算在當前勝率與盈虧比下，最科學的「下注比例」。若為 0% 代表該策略目前無優勢。
        """)
