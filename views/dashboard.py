import streamlit as st
import pandas as pd
import numpy as np

def calculate_max_streak(data):
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
    st.title("📊 雀神數據監控")

    # --- 1. 戰力預測區 (針對 iPhone 優化為卡片式佈局) ---
    st.subheader("🔮 下場預測與手感")
    
    # 在手機端，這四個 column 會自動變成上下排列的卡片
    for p in players:
        data = df_master[p].values
        with st.container(border=True): # 使用邊框營造卡片感
            if len(data) >= 3:
                # 統計運算
                weights = np.arange(1, len(data) + 1)
                prediction = np.average(data, weights=weights)
                std_dev = np.std(data)
                lower_bound = prediction - (std_dev * 0.5)
                upper_bound = prediction + (std_dev * 0.5)
                
                last_score = data[-1]
                avg_score = np.mean(data)
                z_score = (last_score - avg_score) / std_dev if std_dev > 0 else 0
                
                # 色彩與狀態
                if z_score > 1: status, color = "🔥 手感火熱", "#ff4b4b"
                elif z_score < -1: status, color = "❄️ 手感冰冷", "#1c83e1"
                else: status, color = "⚖️ 表現穩定", "#7d7d7d"

                # 顯示排版
                col_name, col_val = st.columns([1, 1])
                with col_name:
                    st.markdown(f"### {p}")
                    st.write(status)
                with col_val:
                    st.metric("總結餘", f"${sum(data):,.0f}")

                # --- 放大預測字體 ---
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <p style="margin: 0; font-size: 14px; color: #555;">下場預測金額</p>
                    <h2 style="margin: 0; color: {color}; font-size: 32px;">${prediction:+.1f}</h2>
                    <p style="margin: 0; font-size: 12px; color: #888;">預估範圍: ${lower_bound:.0f} ~ ${upper_bound:.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"⚠️ {p}: 數據不足 (需至少3場)")

    st.divider()

    # --- 2. 趨勢圖 (針對手機調整高度) ---
    st.subheader("📈 歷史戰鬥力走勢")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    # 在手機上高度不宜太高，方便滑動
    st.line_chart(cumulative_df, height=300)

    # --- 3. 專業統計表 (使用 DataFrame 讓手機可以左右滑動) ---
    st.divider()
    st.subheader("📋 深度統計指標")
    
    stats_list = []
    for p in players:
        p_data = df_master[p]
        win_days = (p_data > 0).sum()
        total_days = len(p_data)
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        
        stats_list.append({
            "玩家": p,
            "勝率": f"{(win_days/total_days*100):.1f}%",
            "穩定": f"{stability:.2f}",
            "連勝": f"{calculate_max_streak(p_data)}場",
            "EV": f"${p_data.mean():.1f}"
        })
    
    # 手機端使用 dataframe 比 table 好，因為支援橫向滾動
    st.dataframe(pd.DataFrame(stats_list).set_index("玩家"), use_container_width=True)

    # --- 預測方法備註 ---
    with st.expander("ℹ️ 預測模型說明"):
        st.caption("採用 WMA 加權移動平均與 0.5σ 標準差區間計算。")
