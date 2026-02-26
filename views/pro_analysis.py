import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險與量化績效審計</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #566573;'>專業量化研究部 | 損益頻率密度精細化報告 (-500 to +500)</p>", unsafe_allow_html=True)
    
    if len(df_master) < 5:
        st.warning("⚠️ 數據量不足：量化分佈分析需至少 5 場數據。")
        return

    # --- 1. 核心計量矩陣 ---
    st.subheader("📑 核心風險與回報指標")
    
    quant_metrics = []
    player_data_dict = {}

    for p in players:
        series = pd.to_numeric(df_master[p], errors='coerce').fillna(0)
        player_data_dict[p] = series
        
        # 統計運算
        mean_val = series.mean()
        vol = series.std()
        sharpe = (mean_val / vol) if vol > 0 else 0
        skew = series.skew()
        kurt = series.kurt()
        mdd = (series.cumsum() - series.cumsum().cummax()).min()

        quant_metrics.append({
            "資產標的 (Player)": p,
            "期望回報 (Mean)": mean_val,
            "波動度 (σ)": vol,
            "夏普比率 (Sharpe)": sharpe,
            "偏度 (Skew)": skew,
            "峰度 (Kurt)": kurt,
            "最大回撤 (MDD)": mdd
        })

    df_quant = pd.DataFrame(quant_metrics).set_index("資產標的 (Player)")
    st.dataframe(df_quant.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["夏普比率 (Sharpe)"]), use_container_width=True)

    # --- 2. 高解析度損益分佈圖 (-500 to +500) ---
    st.divider()
    st.subheader("📊 損益頻率分佈 (High-Resolution Density)")
    
    # 設置涵蓋 -500 到 +500 的 11 個專業級距
    bins = [-float('inf'), -500, -300, -100, -50, 0, 50, 100, 300, 500, float('inf')]
    labels = ["<-500", "-500~-300", "-300~-100", "-100~-50", "-50~0", "0~50", "50~100", "100~300", "300~500", ">500"]

    # 採用單行顯示，確保 X 軸標籤不擠迫
    for p in players:
        st.markdown(f"<div style='padding:10px; background:#F2F4F4; border-radius:8px; font-weight:bold; color:#1B4F72; border-left: 5px solid #1B4F72; margin-bottom:5px;'>📈 資產績效分佈：{p}</div>", unsafe_allow_html=True)
        
        data = player_data_dict[p]
        # 計算各區間頻率
        dist_df = pd.cut(data, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
        
        # 繪製長條圖
        st.bar_chart(dist_df, color="#2E86C1")
        st.caption(f"樣本總數 n={len(data)} | 當前區間分布計數")
        st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. 策略分類與風險評註 ---
    st.divider()
    st.subheader("🏗️ 投資策略行為特徵")
    
    prof_cols = st.columns(2)
    for i, p in enumerate(players):
        s_ratio = df_quant.loc[p, "夏普比率 (Sharpe)"]
        sk_val = df_quant.loc[p, "偏度 (Skew)"]
        kt_val = df_quant.loc[p, "峰度 (Kurt)"]
        
        # 精準策略歸類
        if s_ratio > 0.8:
            strategy, accent = "系統性盈利 (Alpha Generation)", "#28B463"
            risk_desc = "分佈高度右偏且集中。獲利效率極高，具備可重複的技術優勢。"
        elif abs(df_quant.loc[p, "最大回撤 (MDD)"]) > 500:
            strategy, accent = "高槓桿風險 (High Leverage)", "#E67E22"
            risk_desc = "MDD 突破 500 點大關。分佈圖出現極端尾部事件，風險管理需加強。"
        elif sk_val > 1.2 or kt_val > 2.0:
            strategy, accent = "高凸性策略 (High Convexity)", "#F1C40F"
            risk_desc = "分佈呈現肥尾 (Fat-tails)。典型「平時小輸、偶爾大贏」的獲利特徵。"
        else:
            strategy, accent = "市場中性/追隨者 (Market Neutral)", "#5D6D7E"
            risk_desc = "損益集中在中心區間 (-100~100)，缺乏極端獲利爆發力。"

        with prof_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#FDFEFE; border: 1px solid #EAECEE; border-left: 6px solid {accent}; padding:20px; border-radius:4px; margin-bottom:15px; min-height:140px;">
                    <p style="margin:0; font-size:11px; color:#99A3A3; font-weight:bold; letter-spacing:1px;">STRATEGY ID: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:18px; font-weight:bold; color:#2C3E50;">{strategy}</p>
                    <p style="margin:0; font-size:13px; color:#566573; line-height:1.5;">{risk_desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 統計學手冊 ---
    st.divider()
    with st.expander("🔬 如何解讀 -500/+500 高解析度分佈圖？"):
        st.markdown("""
        * **中心化趨勢 (-50~50)**：如果大部份數據落在這個區間，代表該玩家屬於「防守型/技術型」，不輕易放銃或大贏。
        * **肥尾效應 (Fat Tails)**：觀察 `<-500` 或 `>500` 的柱狀。如果頻率顯著，代表該玩家參與了「高賠率事件」（如天胡、大三元、包自摸）。
        * **偏度 (Skewness)**：衡量「不對稱性」。
            * **正偏 (Positive)**：右側長尾，代表有能力贏得超大局。
            * **負偏 (Negative)**：左側長尾，代表容易遇到「災難性虧損」。
        """)
