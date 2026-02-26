import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠 專業數據深度建模</h2>", unsafe_allow_html=True)
    
    if len(df_master) < 3:
        st.warning("數據量不足（需至少 3 次紀錄）以進行專業建模分析。")
        return

    # --- 1. 穩定度與風險特徵 (Consistency & Risk) ---
    st.subheader("🛡️ 穩定度與風險特徵")
    
    pro_stats = {}
    for p in players:
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 變異係數 (Coefficient of Variation) - 越小代表表現越穩定
        cv = (std / abs(avg)) if avg != 0 else np.nan
        
        # 最大回撤 (Max Drawdown) - 從巔峰跌落的最大值
        cumsum = data.cumsum()
        running_max = cumsum.cummax()
        drawdown = (cumsum - running_max).min()

        pro_stats[p] = {
            "穩定係數 (CV)": cv,
            "最大回撤 (Max DD)": drawdown,
            "單日平均波幅": std,
            "獲利穩定度": "高" if std < 100 else "中" if std < 200 else "低"
        }

    df_pro = pd.DataFrame(pro_stats).T
    st.dataframe(df_pro.style.format(precision=2), use_container_width=True)
    
    st.info("💡 **穩定係數 (CV)** 越低，代表你每一場的表現越接近平均值。**最大回撤** 反映了你曾經「輸最勁」的連續虧損。")
    st.divider()

    # --- 2. 玩家屬性雷達圖數據 (Attribute Matrix) ---
    st.subheader("🎭 玩家屬性特徵")
    
    # 建立一個屬性矩陣
    attr_list = []
    for p in players:
        data = df_master[p]
        # 風格判定邏輯
        risk_style = "激進派 (Aggressive)" if data.std() > 200 else "穩健派 (Conservative)"
        earning_style = "爆發型" if data.max() > 400 else "細水長流"
        
        attr_list.append({
            "玩家": p,
            "風險風格": risk_style,
            "得分模式": earning_style,
            "單日最高": int(data.max()),
            "單日最低": int(data.min())
        })
    
    st.table(pd.DataFrame(attr_list).set_index("玩家"))
    st.divider()

    # --- 3. Z-Score 異動檢測 (Anomaly Detection) ---
    st.subheader("🚨 最近對局異動分析 (Z-Score)")
    
    last_row = df_master.iloc[-1]
    z_results = []
    for p in players:
        avg = df_master[p].mean()
        std = df_master[p].std()
        z_score = (last_row[p] - avg) / std if std > 0 else 0
        
        status = "正常發揮"
        if z_score > 1.5: status = "🎉 超水準爆發"
        elif z_score < -1.5: status = "💀 嚴重失準"
        
        z_results.append({"玩家": p, "Z-Score": z_score, "評價": status})
    
    z_cols = st.columns(2)
    for i, res in enumerate(z_results):
        with z_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#f0f2f6; padding:10px; border-radius:10px; margin-bottom:10px; text-align:center;">
                    <p style="margin:0; font-size:14px; font-weight:bold;">{res['玩家']}</p>
                    <p style="margin:2px 0; font-size:24px; font-weight:900; color:#000;">{res['Z-Score']:.2f}</p>
                    <p style="margin:0; font-size:12px; color:#555;">{res['評價']}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 專業術語 Markdown ---
    with st.expander("🔬 專業分析術語解釋"):
        st.markdown("""
        * **Z-Score (標準分數)**: 
            * 公式：$(x - \mu) / \sigma$
            * 意義：衡量該次表現偏離平均值的程度。Z-Score 為 2 代表你比 95% 的對局都要好。
        * **Max Drawdown (最大回撤)**: 
            * 衡量你的錢包「最黑暗的時刻」。
        * **Coefficient of Variation (穩定係數)**: 
            * 數值越低，代表實力越穩定，較少受運氣波動影響。
        """)
