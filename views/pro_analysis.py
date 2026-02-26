import streamlit as st
import pandas as pd

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險與量化績效審計</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #566573;'>專業量化研究部 | 波動率調整後收益分析報告</p>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據觀測值不足：需至少 5 筆對局紀錄以符合漸近法向分佈（Asymptotic Normality）之假設。")
        return

    # --- 1. 量化績效矩陣 (Quantitative Performance Matrix) ---
    st.subheader("📑 核心風險與回報指標")
    
    quant_metrics = []
    for p in players:
        # 數據向量化處理
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        
        # 統計量計算
        mean_val = series.mean()
        volatility = series.std()
        
        # 1. 夏普比率 (Sharpe Ratio) - 衡量單位風險的超額回報
        sharpe = (mean_val / volatility) if volatility > 0 else 0
        
        # 2. 偏度 (Skewness) - 衡量獲利分佈的對稱性
        skew = series.skew()
        
        # 3. 峰度 (Kurtosis) - 衡量極端事件（尾部風險）的發生機率
        kurt = series.kurt()
        
        # 4. 最大回撤 (Maximum Drawdown) - 衡量資本侵蝕的最壞情況
        cum_sum = series.cumsum()
        running_max = cum_sum.cummax()
        mdd = (cum_sum - running_max).min()

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
    
    # 呈現機構級熱力圖表格
    st.dataframe(
        df_quant.style.format(precision=2)
        .background_gradient(cmap="RdYlGn", subset=["夏普比率 (Sharpe)"])
        .background_gradient(cmap="Reds_r", subset=["年化波動度 (σ)", "最大回撤 (MDD)"]),
        use_container_width=True
    )

    # --- 2. 精算學風險分類 (Actuarial Profiling) ---
    st.divider()
    st.subheader("🏗️ 投資策略特徵分類")
    
    prof_cols = st.columns(2)
    for i, p in enumerate(players):
        # 讀取計算指標
        s_ratio = df_quant.loc[p, "夏普比率 (Sharpe)"]
        sk_val = df_quant.loc[p, "獲利偏度 (Skew)"]
        kt_val = df_quant.loc[p, "獲利峰度 (Kurt)"]
        
        # 策略歸類邏輯
        if s_ratio > 0.8:
            strategy, accent = "超額阿爾法策略 (Alpha Generation)", "#28B463"
            risk_desc = "具備極高獲利效率，對運氣成分依賴度低，穩定性極強。"
        elif sk_val > 1.2:
            strategy, accent = "長倉波動率策略 (Long Volatility)", "#F1C40F"
            risk_desc = "回報高度依賴正向尾部風險，傾向於捕捉極大牌型（大數定律）。"
        elif kt_val > 2.5:
            strategy, accent = "肥尾風險敞口 (Leptokurtic Risk)", "#E74C3C"
            risk_desc = "具備極端不確定性，容易出現連環出銃等系統性風險（黑天鵝）。"
        else:
            strategy, accent = "指數追蹤策略 (Market Beta)", "#5D6D7E"
            risk_desc = "績效趨向市場平均水平，缺乏顯著的主動獲利能力。"

        with prof_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#FDFEFE; border: 1px solid #EAECEE; border-left: 6px solid {accent}; padding:20px; border-radius:4px; margin-bottom:15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.02);">
                    <p style="margin:0; font-size:11px; color:#99A3A3; letter-spacing:1px; font-weight:bold;">資產識別碼: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:18px; font-weight:700; color:#2C3E50;">{strategy}</p>
                    <p style="margin:0; font-size:13px; color:#566573;"><b>風險評註：</b> {risk_desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 3. 量化分析方法論說明 ---
    st.divider()
    with st.expander("📝 統計學定義與計量邏輯說明"):
        st.markdown("""
        ### 量化指標說明 (Glossary)
        * **夏普比率 (Sharpe Ratio)**：衡量每單位波動所換取的超額收益。比率越高，代表該玩家技巧愈穩定。
        * **獲利偏度 (Skewness)**：衡量獲利分佈的偏斜度。**正偏 (Positive Skew)** 代表具備大贏的爆發力；**負偏 (Negative Skew)** 則代表穩定小贏但潛藏一次大賠的風險。
        * **獲利峰度 (Kurtosis)**：衡量分佈的「肥尾」。高峰度代表該玩家容易遇到「極端對局結果」（即 Black Swan 事件）。
        * **最大回撤 (Max Drawdown)**：衡量從歷史最高獲利點到最低點的最大跌幅，是衡量心理承受力與風險控管的終極指標。
        """)
        
        st.write("---")
        st.caption("免責聲明：本報告數據純屬量化研究性質，投資者（玩家）應審慎管理資本。")
