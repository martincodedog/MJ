import streamlit as st
import pandas as pd

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠雀神進階建模</h2>", unsafe_allow_html=True)
    
    if len(df_master) < 3:
        st.warning("📊 樣本容量不足以啟動 AI 建模。請累積至少 3 場對局數據。")
        return

    # --- 1. 核心計量矩陣 (Core Metrics) ---
    st.subheader("⚔️ 戰力計量指標")
    
    # 利用 Pandas 2.2.3 進行向量化統計
    stats_list = []
    for p in players:
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 盈利效率 (Sharpe Ratio 變體): 每一單位風險能換多少回報
        sharpe = (avg / std) if std > 0 else 0
        
        # 獲利偏度 (Skewness): 判斷是「細水長流」還是「爆發型」
        # Pandas 內建 skew() 已經足夠精準
        sk = data.skew()
        
        # 最大回撤 (Max Drawdown): 衡量最長連輸或最慘跌幅
        cumsum = data.cumsum()
        mdd = (cumsum - cumsum.cummax()).min()

        stats_list.append({
            "玩家": p,
            "盈利效率 (Sharpe)": sharpe,
            "穩定度 (Std)": std,
            "獲利偏度 (Skew)": sk,
            "最大回撤": mdd
        })

    df_pro = pd.DataFrame(stats_list).set_index("玩家")
    st.dataframe(
        df_pro.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["盈利效率 (Sharpe)"]), 
        use_container_width=True
    )

    # --- 2. AI 戰力屬性卡 (特大字體設計) ---
    st.divider()
    st.subheader("🎭 AI 戰力角色標籤")
    
    attr_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        sk_val = data.skew() or 0
        avg_val = data.mean()
        
        # 動態角色邏輯
        if avg_val > 0 and sk_val > 0.5:
            role, color = "🚀 火箭手", "#ff4b4b"
            desc = "極高爆發力，擅長一局定江山。"
        elif avg_val > 0 and sk_val <= 0.5:
            role, color = "🏦 銀行家", "#1e8e3e"
            desc = "穩健獲利，防守極度嚴密。"
        elif avg_val <= 0 and sk_val > 0.5:
            role, color = "🎰 賭徒", "#ffa421"
            desc = "波動巨大，期待下一局翻身。"
        else:
            role, color = "🛡️ 鐵壁", "#00c0f2"
            desc = "輸得很少，但缺乏主動進攻性。"

        with attr_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#ffffff; border:2px solid #f0f2f6; padding:20px; border-radius:20px; margin-bottom:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align:center;">
                    <p style="margin:0; font-size:18px; color:#555; font-weight:bold;">{p}</p>
                    <p style="margin:8px 0; font-size:28px; font-weight:900; color:{color};">{role}</p>
                    <p style="margin:0; font-size:14px; color:#888;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

    # 底部專業數據解釋
    with st.expander("🔬 統計學名詞解釋 (Pro Methodology)"):
        st.markdown("""
        * **盈利效率 (Sharpe)**: 衡量風險回報比。數值越高，代表你是靠實力穩定獲利，而非純靠運氣。
        * **獲利偏度 (Skewness)**: 
            * **正偏 (Positive)**: 經常小虧，但有捕捉大牌（如十三么、大四喜）的能力。
            * **負偏 (Negative)**: 雖然穩定，但一旦出銃大牌就會面臨巨大虧損。
        """)
