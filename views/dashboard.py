import streamlit as st
import pandas as pd
import numpy as np

def calculate_max_streak(data):
    max_streak, current_streak = 0, 0
    for val in data:
        if val > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return max_streak

def show_dashboard(df_master, players):
    # 標題改為置中且精簡
    st.markdown("<h2 style='text-align: center;'>🎣 雀界即時戰況</h2>", unsafe_allow_html=True)

    # --- 1. 縱向戰力卡片 (iPhone 必備) ---
    for p in players:
        data = df_master[p].values
        if len(data) >= 3:
            # 統計運算
            weights = np.arange(1, len(data) + 1)
            prediction = np.average(data, weights=weights)
            std_dev = np.std(data)
            total_sum = sum(data)
            
            # 手感評級
            z_score = (data[-1] - np.mean(data)) / std_dev if std_dev > 0 else 0
            if z_score > 1: status, color = "🔥 極度亢奮", "#FF4B4B"
            elif z_score < -1: status, color = "❄️ 手感冰冷", "#1C83E1"
            else: status, color = "⚖️ 走勢平穩", "#31333F"

            # 針對 iPhone 螢幕設計的大字體卡片
            st.markdown(f"""
            <div style="
                border-radius: 15px; 
                padding: 20px; 
                margin-bottom: 15px; 
                background-color: #ffffff;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
                border-left: 10px solid {color};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 20px; font-weight: bold; color: #333;">{p}</span>
                    <span style="font-size: 14px; font-weight: bold; color: {color};">{status}</span>
                </div>
                <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: flex-end;">
                    <div>
                        <p style="margin: 0; font-size: 12px; color: #888;">總結餘</p>
                        <p style="margin: 0; font-size: 32px; font-weight: 900; color: #111;">${total_sum:,.0f}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-size: 12px; color: #888;">下場預測</p>
                        <p style="margin: 0; font-size: 24px; font-weight: 800; color: {color};">${prediction:+.1f}</p>
                    </div>
                </div>
                <div style="margin-top: 15px; background-color: #f8f9fb; padding: 10px; border-radius: 8px; text-align: center;">
                    <span style="font-size: 12px; color: #666;">波動區間：<b>${prediction-(std_dev*0.5):.0f} ～ ${prediction+(std_dev*0.5):.0f}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ {p}: 數據不足")

    st.divider()

    # --- 2. 走勢圖 (調整高度適合手機) ---
    st.markdown("#### 📈 累計損益曲線")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    st.line_chart(cumulative_df, height=250)

    # --- 3. 深度數據表 (使用 st.dataframe 支援左右滑動) ---
    st.markdown("#### 📋 核心指標 (左右滑動查看)")
    stats_list = []
    for p in players:
        p_data = df_master[p]
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        stats_list.append({
            "玩家": p,
            "勝率": f"{( (p_data > 0).sum()/len(p_data)*100 ):.0f}%",
            "穩度": f"{stability:.2f}",
            "連勝": f"{calculate_max_streak(p_data)}",
            "EV": f"{p_data.mean():.0f}"
        })
    
    # iPhone 上 st.table 會變形，用 st.dataframe 並設定 stretch 較好
    st.dataframe(
        pd.DataFrame(stats_list).set_index("玩家"), 
        width='stretch'
    )

    with st.expander("🔬 模型備註"):
        st.caption("採 WMA 加權移動平均，近期戰績權重較高。預測範圍以 0.5σ 計算。")
