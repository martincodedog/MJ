import streamlit as st
import pandas as pd
import numpy as np

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center; color: #1C2833;'>🏛️ 雀壇資產風險與量化績效審計</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #566573;'>專業量化研究部 | 損益頻率密度精細化報告</p>", unsafe_allow_html=True)
    
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

    # --- 2. 高解析度損益分佈圖 (Fine-grained Distribution) ---
    st.divider()
    st.subheader("📊 損益頻率分佈 (High-Resolution Win-Loss Density)")
    
    # 設置更精細的 10 個區間
    # 區間涵蓋：大賠、中賠、小賠、微賠、微贏、小贏、中贏、大贏、極端贏
    bins = [-float('inf'), -50, -30, -20, -10, 0, 10, 20, 30, 50, float('inf')]
    labels = ["<-50", "-50~-30", "-30~-20", "-20~-10", "-10~0", "0~10", "10~20", "20~30", "30~50", ">50"]

    # 繪製圖表：每列兩個玩家，增加視覺寬度
    for i in range(0, len(players), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(players):
                p = players[i + j]
                with cols[j]:
                    st.markdown(f"<div style='text-align:center; padding:5px; background:#F8F9F9; border-radius:5px; font-weight:bold; color:#2C3E50;'>{p}</div>", unsafe_allow_html=True)
                    
                    # 計算頻率
                    data = player_data_dict[p]
                    dist_df = pd.cut(data, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
                    
                    # 使用 st.bar_chart 渲染
                    st.bar_chart(dist_df, color="#1E88E5")
                    st.caption(f"數據分佈 (n={len(data)})")

    # --- 3. 策略分類與風險評註 ---
    st.divider()
    st.subheader("🏗️ 投資策略行為特徵")
    
    prof_cols = st.columns(2)
    for i, p in enumerate(players):
        s_ratio = df_quant.loc[p, "夏普比率 (Sharpe)"]
        sk_val = df_quant.loc[p, "偏度 (Skew)"]
        kt_val = df_quant.loc[p, "峰度 (Kurt)"]
        
        # 歸類邏輯
        if s_ratio > 0.8:
            strategy, accent = "系統性盈利 (Alpha)", "#28B463"
            risk_desc = "分佈高度右偏且集中。獲利效率極高，具備可重複的技術優勢。"
        elif sk_val > 1.2 or kt_val > 2.0:
            strategy, accent = "高凸性策略 (High Convexity)", "#F1C40F"
            risk_desc = "分佈呈現肥尾 (Fat-tails)。依賴偶爾的大幅盈利來覆蓋頻繁的小幅虧損。"
        elif kt_val < 0:
            strategy, accent = "低波動平穩型 (Uniform Return)", "#5D6D7E"
            risk_desc = "損益分佈較為平均，缺乏爆發力，處於市場追隨者狀態。"
        else:
            strategy, accent = "高不確定性 (High Uncertainty)", "#E74C3C"
            risk_desc = "分佈極散。標準差過高，存在顯著的系統性出銃風險。"

        with prof_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#FDFEFE; border: 1px solid #EAECEE; border-left: 6px solid {accent}; padding:20px; border-radius:4px; margin-bottom:15px;">
                    <p style="margin:0; font-size:11px; color:#99A3A3; font-weight:bold;">STRATEGY ID: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:18px; font-weight:bold; color:#2C3E50;">{strategy}</p>
                    <p style="margin:0; font-size:13px; color:#566573;">{risk_desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 統計學手冊 ---
    st.divider()
    with st.expander("🔬 如何解讀高解析度分佈圖？"):
        st.markdown("""
        * **中心化趨勢**：如果中間長條（-10~10）最高，代表該玩家打法保守，屬於「防守型」。
        * **極端尾部 (Tail Events)**：如果兩端（<-50 或 >50）有明顯長條，代表該玩家參與了高槓桿（如：大胡、包自摸）的對局，屬於「爆發型」。
        
        * **偏度 (Skewness)**：正數越大，代表獲利空間越具想像力；負數越大，代表經常遭遇慘賠。
        """)
