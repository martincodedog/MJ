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
    # Use a smaller header for mobile
    st.markdown("### 📊 雀神監控")

    # --- 1. Compact Prediction Tiles ---
    # We use columns to keep things side-by-side even on some larger phones
    # On small iPhones, they will stack, but we've reduced the padding.
    
    for p in players:
        data = df_master[p].values
        with st.container():
            if len(data) >= 3:
                # Math Logic
                weights = np.arange(1, len(data) + 1)
                prediction = np.average(data, weights=weights)
                std_dev = np.std(data)
                
                # Z-Score for Status Color
                z_score = (data[-1] - np.mean(data)) / std_dev if std_dev > 0 else 0
                color = "#FF4B4B" if z_score > 1 else "#1C83E1" if z_score < -1 else "#31333F"
                status_icon = "🔥" if z_score > 1 else "❄️" if z_score < -1 else "⚖️"

                # Compact HTML Card
                st.markdown(f"""
                <div style="
                    border: 1px solid #e6e9ef; 
                    border-radius: 8px; 
                    padding: 10px; 
                    margin-bottom: 8px; 
                    background-color: white;
                    box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 16px;">{p} {status_icon}</span>
                        <span style="font-size: 14px; color: #666;">總結餘: <b>${sum(data):,.0f}</b></span>
                    </div>
                    <div style="margin-top: 5px; display: flex; align-items: baseline;">
                        <span style="font-size: 12px; color: #888; margin-right: 8px;">下場預測:</span>
                        <span style="font-size: 22px; font-weight: 800; color: {color};">${prediction:+.1f}</span>
                        <span style="font-size: 11px; color: #aaa; margin-left: auto;">
                            範圍: {prediction-(std_dev*0.5):.0f}~{prediction+(std_dev*0.5):.0f}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption(f"⚠️ {p}: 數據不足")

    # --- 2. Chart Section (Miniature) ---
    st.markdown("#### 📈 走勢")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    # Shorter height to save vertical space on mobile
    st.line_chart(cumulative_df, height=200)

    # --- 3. Compact KPI Table ---
    st.markdown("#### 📋 指標")
    stats_list = []
    for p in players:
        p_data = df_master[p]
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        stats_list.append({
            "玩家": p,
            "勝率": f"{( (p_data > 0).sum()/len(p_data)*100 ):.0f}%",
            "穩": f"{stability:.1f}",
            "連": f"{calculate_max_streak(p_data)}",
            "EV": f"{p_data.mean():.0f}"
        })
    
    # Using st.dataframe with a small height
    st.dataframe(
        pd.DataFrame(stats_list).set_index("玩家"), 
        use_container_width=True,
        height=175
    )
