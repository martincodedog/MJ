import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def show_dashboard(df_master, players):
    st.title("📊 雀神專業數據分析")

    # --- 1. Advanced Metrics & Prediction ---
    st.subheader("🔮 戰力預測與狀態分析")
    m_cols = st.columns(4)

    for i, p in enumerate(players):
        data = df_master[p].values
        if len(data) >= 3:
            # Calculation: Simple Moving Average (SMA) of last 5 games
            recent_avg = np.mean(data[-5:])
            # Standard Deviation for Range
            std_dev = np.std(data)
            
            # Prediction Logic: Weighted Average + Volatility Range
            weights = np.arange(1, len(data) + 1)
            prediction = np.average(data, weights=weights)
            lower_bound = prediction - (std_dev * 0.5) # 0.5 sigma for tighter range
            upper_bound = prediction + (std_dev * 0.5)
            
            # Z-Score: How "weird" was the last game?
            last_score = data[-1]
            z_score = (last_score - np.mean(data)) / std_dev if std_dev > 0 else 0
            status = "🔥 狀態火熱" if z_score > 1 else "❄️ 手感冰冷" if z_score < -1 else "⚖️ 表現穩定"

            with m_cols[i]:
                st.metric(label=f"{p} 累積結餘", value=f"${sum(data):,.0f}")
                st.write(f"**下場預測:** `${prediction:+.1f}`")
                st.caption(f"預估區間: `${lower_bound:.0f}` ~ `${upper_bound:.0f}`")
                st.info(status)
        else:
            m_cols[i].write(f"{p}: 數據不足")

    st.divider()

    # --- 2. Comparative Cumulative Chart ---
    st.subheader("📈 歷史戰鬥力走勢 (累計)")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    st.line_chart(cumulative_df)

    # --- 3. Deep Statistical KPIs ---
    st.divider()
    st.subheader("📋 專業指標 (Advanced KPIs)")
    
    stats_list = []
    for p in players:
        p_data = df_master[p]
        win_days = (p_data > 0).sum()
        total_days = len(p_data)
        
        # Sharpe Ratio (Simplified): Reward per unit of risk
        # We use Avg / StdDev to see who is the most "efficient" winner
        sharpe = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        
        stats_list.append({
            "玩家": p,
            "勝率 (Win Rate)": f"{(win_days/total_days*100):.1f}%",
            "獲利波動 ($\sigma$)": f"{p_data.std():.1f}",
            "穩定係數 (Sharpe)": f"{sharpe:.2f}",
            "連勝/連敗紀錄": f"{calculate_max_streak(p_data)}",
            "期望值 (EV)": f"${p_data.mean():.1f}"
        })
    
    st.table(pd.DataFrame(stats_list).set_index("玩家"))

def calculate_max_streak(data):
    """Calculates the maximum winning streak."""
    max_streak = 0
    current_streak = 0
    for val in data:
        if val > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return f"{max_streak} 連勝"
