import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠 雀神 AI 進階建模</h2>", unsafe_allow_html=True)
    
    if len(df_master) < 3:
        st.warning("數據量不足，請累積至少 3 次對局紀錄以進行深度建模。")
        return

    # --- 1. 核心競爭力矩陣 (Core Competency Matrix) ---
    st.subheader("⚔️ 核心競爭力指標")
    
    pro_stats = {}
    for p in players:
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 1. 盈利效率 (Sharpe Ratio 變體)
        sharpe = (avg / std) if std > 0 else 0
        
        # 2. 手動計算偏度 (Skewness) - 不使用 scipy
        # Formula: Σ(x - μ)^3 / (N * σ^3)
        n = len(data)
        if n > 2 and std > 0:
            skew_val = (n / ((n - 1) * (n - 2))) * (((data - avg) ** 3).sum() / (std ** 3))
        else:
            skew_val = 0
            
        # 3. 最大回撤 (Max Drawdown)
        cumsum = data.cumsum()
        running_max = cumsum.cummax()
        drawdown = (cumsum - running_max).min()

        pro_stats[p] = {
            "盈利效率": sharpe,
            "波動穩定度": std,
            "獲利偏度": skew_val,
            "最大回撤": drawdown,
            "正分天數": (data > 0).sum()
        }

    df_pro = pd.DataFrame(pro_stats).T
    st.dataframe(
        df_pro.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["盈利效率"]), 
        use_container_width=True
    )
    st.divider()

    # --- 2. AI 戰力五維模型 (Five-Dimension Card) ---
    st.subheader("🛡️ 玩家五維屬性卡")
    
    attr_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        
        # 標準化各項指標 (0-100)
        atk = min(100, int((data.max() / 500) * 100))        # 最高得分
        dfs = max(0, int(100 - (abs(data.min()) / 500) * 100)) # 最低失分
        stb = max(0, int(100 - (data.std() / 300) * 100))    # 標準差倒數
        lck = int((pro_stats[p]["獲利偏度"] + 2) / 4 * 100)   # 偏度映射
        end = int((data >= 0).sum() / len(data) * 100)       # 勝率
        
        with attr_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#ffffff; border:2px solid #eee; padding:15px; border-radius:20px; margin-bottom:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
                    <p style="margin:0; font-size:16px; color:#1f77b4; font-weight:bold; text-align:center;">{p}</p>
                    <hr style="margin:8px 0;">
                    <p style="margin:0; font-size:12px; color:#666;">🔥 <b>進攻 (ATK):</b> {atk}</p>
                    <p style="margin:0; font-size:12px; color:#666;">🛡️ <b>防守 (DFS):</b> {dfs}</p>
                    <p style="margin:0; font-size:12px; color:#666;">⚖️ <b>穩定 (STB):</b> {stb}</p>
                    <p style="margin:0; font-size:12px; color
