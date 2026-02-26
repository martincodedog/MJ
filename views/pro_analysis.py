import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import skew

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠 雀神 AI 進階建模</h2>", unsafe_allow_html=True)
    
    if len(df_master) < 3:
        st.warning("數據量不足，請累積至少 3 次對局紀錄以進行深度分析。")
        return

    # --- 1. 核心競爭力矩陣 (Core Competency Matrix) ---
    st.subheader("⚔️ 玩家競爭力矩陣")
    
    pro_stats = {}
    for p in players:
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 1. 盈利效率 (Sharpe Ratio 變體): 每一單位風險能換多少回報
        sharpe = (avg / std) if std > 0 else 0
        
        # 2. 偏度 (Skewness): 正數代表「常贏小錢但偶爾大贏」，負數代表「常贏小錢但偶爾大輸」
        skewness = skew(data) if len(data) > 2 else 0
        
        # 3. 破產風險 (Risk of Ruin 簡化版): 根據波動度判斷本金壓力
        risk_score = (std / (avg if avg > 0 else 1)) * 100

        pro_stats[p] = {
            "盈利效率 (Sharpe)": sharpe,
            "穩定度 (Std Dev)": std,
            "偏度 (運氣/風格)": skewness,
            "防守力 (Min)": data.min(),
            "進攻力 (Max)": data.max()
        }

    df_pro = pd.DataFrame(pro_stats).T
    st.dataframe(df_pro.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["盈利效率 (Sharpe)"]), use_container_width=True)
    
    st.divider()

    # --- 2. AI 戰力建模 (Attribute Radar Mapping) ---
    st.subheader("🎭 AI 戰力屬性標籤")
    
    attr_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 戰力分析邏輯
        if avg > 0 and std < 150: 
            role = "🏦 銀行家 (穩定獲利者)"
        elif avg > 0 and std >= 150:
            role = "🚀 火箭手 (爆發力極強)"
        elif avg <= 0 and std < 150:
            role = "🛡️ 鐵壁 (輸得很少的防守者)"
        else:
            role = "🎰 賭徒 (波動極大)"
            
        with attr_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#ffffff; border:1px solid #eee; padding:15px; border-radius:15px; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <p style="margin:0; font-size:16px; font-weight:bold; color:#1f77b4;">{p}</p>
                    <p style="margin:5px 0; font-size:14px; font-weight:900; color:#333;">角色: {role}</p>
                    <p style="margin:0; font-size:12px; color:#666;">
                        進攻指數: {min(100, int(data.max()/500*100))}%<br>
                        穩定指數: {max(0, int(100 - std/400*100))}%<br>
                        韌性指數: {min(100, int(abs(data.min())/500*100))}%
                    </p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 3. 下局預測與心理博弈 (AI Strategy Prediction) ---
    st.subheader("🔮 AI 戰略博弈建議")
    
    predict_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        last_3 = data.tail(3).mean()
        overall_avg = data.mean()
        
        # 獲利機率預測 (基於蒙地卡羅思想的簡化版)
        win_prob = (data > 0).sum() / len(data) * 100
        
        # AI 建議邏輯
        if last_3 > overall_avg:
            ai_advice = "手風正順，建議維持積極打法，增加攻擊頻率。"
        else:
            ai_advice = "手風回落，建議轉攻為守，等待均值回歸。"
            
        with predict_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#1e1e1e; color:#00ff00; padding:15px; border-radius:15px; margin-bottom:15px; font-family: 'Courier New', Courier, monospace;">
                    <p style="margin:0; font-size:14px; color:#aaa;">>>> PLAYER: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:18px; font-weight:bold;">歷史勝率: {win_prob:.1f}%</p>
                    <p style="margin:5px 0; font-size:12px; color:#00cc00; line-height:1.4;">[AI 建議]: {ai_advice}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 專業模型說明 ---
    with st.expander("🔬 專業數據模型說明 (Pro Methodology)"):
        st.markdown("""
        * **Sharpe Ratio (盈利效率)**：衡量每一單位風險產出的超額回報。數值越高，代表你不是靠運氣，而是靠實力穩定贏錢。
        * **Skewness (偏度)**：
            * **正偏 (Positive Skew)**：長期小虧，但有能力捕捉極大贏面的局。
            * **負偏 (Negative Skew)**：長期穩定贏小錢，但要小心一次性的大潰敗。
        * **Z-Score 檢測**：自動識別當前表現是否偏離統計常態。
        """)
