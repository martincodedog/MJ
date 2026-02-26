import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險與量化績效審計</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #566573;'>專業量化研究部 | 波動率調整後收益分析報告</p>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據觀測值不足：需至少 5 筆對局紀錄。")
        return

    # --- 1. 量化績效矩陣 ---
    st.subheader("📑 核心風險與回報指標")
    
    quant_metrics = []
    player_data_dict = {} # 用於後續繪圖

    for p in players:
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        player_data_dict[p] = series
        
        # 統計量計算
        mean_val = series.mean()
        volatility = series.std()
        sharpe = (mean_val / volatility) if volatility > 0 else 0
        skew = series.skew()
        kurt = series.kurt()
        
        cum_sum = series.cumsum()
        mdd = (cum_sum - cum_sum.cummax()).min()

        quant_metrics.append({
            "資產標的 (Player)": p,
            "預期回報 (Mean)": mean_val,
            "年化波動度 (σ)": volatility,
            "夏普比率 (Sharpe)": sharpe,
            "獲利偏度 (Skew)": skew,
            "獲利峰度 (Kurt)": kurt,
            "最大回撤 (MDD)": mdd
        })

    df_quant = pd.DataFrame(quant_metrics).set_index("資產標的 (Player)")
    st.dataframe(df_quant.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["夏普比率 (Sharpe)"]), use_container_width=True)

    # --- 2. 獲利/虧損分佈圖 (取代原本熱力圖表格) ---
    st.divider()
    st.subheader("📊 損益分佈機率密度 (Win-Loss Distribution)")
    
    # 使用 st.columns 為每個玩家建立獨立的小圖表
    chart_cols = st.columns(len(players))
    
    for i, p in enumerate(players):
        with chart_cols[i]:
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{p}</p>", unsafe_allow_html=True)
            
            # 將數據分配到不同的區間 (Bins)
            data = player_data_dict[p]
            
            # 定義區間：例如 每 10 分一個級距
            bins = [-float('inf'), -30, -15, 0, 15, 30, float('inf')]
            labels = ["<-30", "-30~-15", "-15~0", "0~15", "15~30", ">30"]
            
            dist_series = pd.cut(data, bins=bins, labels=labels).value_counts().sort_index()
            
            # 使用 Streamlit 原生長條圖
            st.bar_chart(dist_series)
            st.caption("頻率分佈 (Frequency)")

    

    # --- 3. 精算學風險分類 ---
    st.divider()
    st.subheader("🏗️ 投資策略特徵分類")
    
    prof_cols = st.columns(2)
    for i, p in enumerate(players):
        s_ratio = df_quant.loc[p, "夏普比率 (Sharpe)"]
        sk_val = df_quant.loc[p, "獲利偏度 (Skew)"]
        kt_val = df_quant.loc[p, "獲利峰度 (Kurt)"]
        
        if s_ratio > 0.8:
            strategy, accent = "超額阿爾法策略 (Alpha Generation)", "#28B463"
            risk_desc = "獲利效率極高，分佈圖呈現明顯右偏，穩定性強。"
        elif sk_val > 1.2:
            strategy, accent = "長倉波動率策略 (Long Volatility)", "#F1C40F"
            risk_desc = "分佈圖具備長尾效應，依賴極端大牌獲利。"
        elif kt_val > 2.5:
            strategy, accent = "肥尾風險敞口 (Leptokurtic Risk)", "#E74C3C"
            risk_desc = "分佈極端，存在高度不確定性，容易出現黑天鵝事件。"
        else:
            strategy, accent = "指數追蹤策略 (Market Beta)", "#5D6D7E"
            risk_desc = "分佈集中在中心區間，缺乏獲利爆發力。"

        with prof_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#FDFEFE; border: 1px solid #EAECEE; border-left: 6px solid {accent}; padding:20px; border-radius:4px; margin-bottom:15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.02);">
                    <p style="margin:0; font-size:11px; color:#99A3A3; letter-spacing:1px; font-weight:bold;">資產識別碼: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:18px; font-weight:700; color:#2C3E50;">{strategy}</p>
                    <p style="margin:0; font-size:13px; color:#566573;"><b>風險評註：</b> {risk_desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 方法論說明 ---
    st.divider()
    with st.expander("📝 統計學定義與計量邏輯說明"):
        st.markdown("""
        ### 指標說明
        * **分佈圖解讀**：長條圖越往右集中代表贏面越大；若兩端（>30 與 <-30）很高則代表打法激進。
        * **夏普比率 (Sharpe Ratio)**：數值越高代表技巧越穩。
        * **獲利偏度 (Skewness)**：正偏（Positive Skew）代表有贏大錢的能力。
        * **獲利峰度 (Kurtosis)**：衡量極端值，峰度高代表這玩家容易「大贏或大輸」。
        """)
