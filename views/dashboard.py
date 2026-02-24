import streamlit as st
import pandas as pd
import numpy as np

def calculate_max_streak(data):
    """計算連續贏錢天數的最大值"""
    max_streak = 0
    current_streak = 0
    for val in data:
        if val > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return max_streak

def show_dashboard(df_master, players):
    st.title("📊 雀神進階數據分析")

    # --- 1. 預測與區間分析 (Prediction & Range) ---
    st.subheader("🔮 戰力預測與手感分析")
    m_cols = st.columns(4)

    for i, p in enumerate(players):
        data = df_master[p].values
        if len(data) >= 3:
            # A. 預測值：使用加權移動平均 (越近期的對局權重越高)
            weights = np.arange(1, len(data) + 1)
            prediction = np.average(data, weights=weights)
            
            # B. 波動範圍：使用標準差 (Standard Deviation)
            # 範圍設定為 預測值 ± (0.5 * 標準差)，代表約 40% 的機率落在該區間
            std_dev = np.std(data)
            lower_bound = prediction - (std_dev * 0.5)
            upper_bound = prediction + (std_dev * 0.5)
            
            # C. Z-Score 狀態判斷 (衡量最後一場對局是否偏離常態)
            last_score = data[-1]
            avg_score = np.mean(data)
            z_score = (last_score - avg_score) / std_dev if std_dev > 0 else 0
            
            if z_score > 1: status = "🔥 手感火熱"
            elif z_score < -1: status = "❄️ 手感冰冷"
            else: status = "⚖️ 表現穩定"

            with m_cols[i]:
                st.metric(label=f"{p} 累積結餘", value=f"${sum(data):,.0f}")
                st.markdown(f"**下場預測:** `${prediction:+.1f}`")
                st.caption(f"預估範圍: `${lower_bound:.0f}` ~ `${upper_bound:.0f}`")
                st.info(status)
        else:
            m_cols[i].write(f"{p}: 數據不足")

    st.divider()

    # --- 2. 累計與單日走勢圖 ---
    st.subheader("📈 戰鬥力走勢 (累積損益)")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    st.line_chart(cumulative_df)

    # --- 3. 專業統計 KPI (表格) ---
    st.divider()
    st.subheader("📋 深度統計指標 (Deep Analytics)")
    
    stats_list = []
    for p in players:
        p_data = df_master[p]
        win_days = (p_data > 0).sum()
        total_days = len(p_data)
        
        # 穩定係數 (Sharpe Ratio 簡化版)：平均回報 / 風險波動
        # 越高代表贏得越穩，低代表大起大落
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        
        stats_list.append({
            "玩家": p,
            "勝率": f"{(win_days/total_days*100):.1f}%",
            "波動風險($\sigma$)": f"{p_data.std():.1f}",
            "穩定係數": f"{stability:.2f}",
            "最高連勝": f"{calculate_max_streak(p_data)} 場",
            "期望值 (EV)": f"${p_data.mean():.1f}"
        })
    
    # 顯示統計表
    st.table(pd.DataFrame(stats_list).set_index("玩家"))

    # --- 4. 單日損益分佈 (Area Chart) ---
    st.divider()
    st.subheader("🌊 單日損益波動")
    st.area_chart(df_master.set_index("Date")[players])
