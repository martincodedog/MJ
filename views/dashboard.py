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

def calculate_max_drawdown(data):
    """計算最大回撤（從最高點跌落最多的金額）"""
    cumulative = np.cumsum(data)
    peak = np.maximum.accumulate(cumulative)
    drawdown = peak - cumulative
    return np.max(drawdown)

def show_dashboard(df_master, players):
    st.markdown("### 🎣 雀界即時戰況 (水魚監控)")

    # --- 1. 專業預測卡片 ---
    for p in players:
        data = df_master[p].values
        if len(data) >= 3:
            # 統計運算
            weights = np.arange(1, len(data) + 1)
            prediction = np.average(data, weights=weights)
            std_dev = np.std(data)
            total_sum = sum(data)
            
            # 手感評級 (基於 Z-Score)
            z_score = (data[-1] - np.mean(data)) / std_dev if std_dev > 0 else 0
            if z_score > 1: status, color = "🔥 極度亢奮", "#FF4B4B"
            elif z_score < -1: status, color = "❄️ 進入冰封", "#1C83E1"
            else: status, color = "⚖️ 走勢平穩", "#31333F"

            # 增加尺寸的 HTML 卡片
            st.markdown(f"""
            <div style="
                border: 1.5px solid #f0f2f6; 
                border-radius: 12px; 
                padding: 15px; 
                margin-bottom: 12px; 
                background-color: #ffffff;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.02);
            ">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 18px; font-weight: bold;">{p} <small style="font-size:12px; color:{color};">{status}</small></span>
                    <span style="font-size: 14px; color: #666;">總結餘</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: -5px;">
                    <span style="font-size: 11px; color: #999;">{len(data)} 場對局紀錄</span>
                    <span style="font-size: 28px; font-weight: 900; color: #111;">${total_sum:,.0f}</span>
                </div>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid #eee;">
                <div style="display: flex; flex-direction: column;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-size: 13px; color: #444;">🎯 下場預測推演</span>
                        <span style="font-size: 24px; font-weight: 800; color: {color};">${prediction:+.1f}</span>
                    </div>
                    <div style="background-color: #f8f9fb; padding: 8px; border-radius: 6px; margin-top: 8px; text-align: center;">
                        <span style="font-size: 12px; color: #666;">合理波動區間</span><br>
                        <span style="font-size: 18px; font-weight: 700; color: #333;">${prediction-(std_dev*0.5):.0f} ～ ${prediction+(std_dev*0.5):.0f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption(f"⚠️ {p}: 數據量不足以進行專業建模")

    # --- 2. 趨勢分析 ---
    st.markdown("#### 📈 累計損益走勢 (Equity Curve)")
    cumulative_df = df_master.set_index("Date")[players].cumsum()
    st.line_chart(cumulative_df, height=250)

    # --- 3. 專業風險指標表 ---
    st.markdown("#### 📋 核心風險指標 (Quant Analysis)")
    stats_list = []
    for p in players:
        p_data = df_master[p]
        # Sharpe Ratio 概念: 平均每場贏多少 / 波動大小
        stability = (p_data.mean() / p_data.std()) if p_data.std() > 0 else 0
        mdd = calculate_max_drawdown(p_data)
        
        stats_list.append({
            "玩家": p,
            "勝率": f"{( (p_data > 0).sum()/len(p_data)*100 ):.0f}%",
            "獲利係數": f"{stability:.2f}",
            "最大回撤": f"${mdd:,.0f}",
            "連勝紀錄": f"{calculate_max_streak(p_data)}",
            "期望值(EV)": f"{p_data.mean():.1f}"
        })
    
    st.dataframe(
        pd.DataFrame(stats_list).set_index("玩家"), 
        use_container_width=True,
        height=180
    )

    # 方法論備註
    with st.expander("🔬 統計方法論"):
        st.caption("預測模型採用 WMA 加權移動平均。風險指標包含 MDD (Max Drawdown) 用於評估該玩家在最倒霉時的承壓能力。範圍區間基於 0.5 個標準差，涵蓋約 40% 的歷史情境。")
