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

    # --- 1. 預測與區間分析 ---
    st.subheader("🔮 戰力預測與手感分析")
    m_cols = st.columns(4)

    for i, p in enumerate(players):
        data = df_master[p].values
        if len(data) >= 3:
            # A. 加權移動平均 (WMA)
            weights = np.arange(1, len(data) + 1)
            prediction = np.average(data, weights=weights)
            
            # B. 波動標準差 (Sigma)
            std_dev = np.std(data)
            lower_bound = prediction - (std_dev * 0.5)
            upper_bound = prediction + (std_dev * 0.5)
            
            # C. Z-Score 狀態
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

    # --- 預測方法備註 ---
    with st.expander("ℹ️ 預測模型說明 (Prediction Methodology)"):
        st.write("""
        本系統採用以下統計模型進行分析：
        1. **加權預測 (WMA)**：並非簡單平均，而是給予**近期對局**更高的權重，反映玩家最近的手感趨勢。
        2. **預估範圍 ($\sigma$)**：基於歷史波動率。範圍越寬，代表該玩家打法較「大出大進」；範圍越窄，代表打法趨於穩健。
        3. **狀態判斷 (Z-Score)**：衡量最後一場表現與長期平均值的離散程度，用以判斷玩家是否處於「連旺」或「連衰」的統計臨界點。
        """)

    st.divider()

    # --- 2. 累計走勢圖 ---
    st.subheader("📈 歷史戰鬥力走勢 (累積損益)")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    st.line_chart(cumulative_df)

    # --- 3. 專業統計 KPI ---
    st.divider()
    st.subheader("📋 深度統計指標 (Deep Analytics)")
    
    stats_list = []
    for p in players:
        p_data = df_master[p]
        win_days = (p_data > 0).sum()
        total_days = len(p_data)
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        
        stats_list.append({
            "玩家": p,
            "勝率": f"{(win_days/total_days*100):.1f}%",
            "波動風險($\sigma$)": f"{p_data.std():.1f}",
            "穩定係數": f"{stability:.2f}",
            "最高連勝": f"{calculate_max_streak(p_data)} 場",
            "期望值 (EV)": f"${p_data.mean():.1f}"
        })
    
    st.table(pd.DataFrame(stats_list).set_index("玩家"))
