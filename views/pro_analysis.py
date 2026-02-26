import streamlit as st
import pandas as pd

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠 雀神 AI 進階建模</h2>", unsafe_allow_html=True)
    
    # 檢查數據量是否足夠計算統計指標 (至少需要 3 次紀錄)
    if len(df_master) < 3:
        st.warning("數據量不足，請累積至少 3 次對局紀錄以進行深度分析。")
        return

    # --- 1. 核心競爭力矩陣 (Competency Matrix) ---
    st.subheader("⚔️ 核心競爭力指標")
    
    pro_stats = {}
    for p in players:
        data = df_master[p]
        avg = data.mean()
        std = data.std()
        
        # 1. 盈利效率 (Sharpe Ratio 變體)
        sharpe = (avg / std) if std > 0 else 0
        
        # 2. 獲利偏度 (Skewness) - 使用 Pandas 內建函數，唔使 scipy/numpy
        sk = data.skew()
        
        # 3. 最大回撤 (Max Drawdown) - 手動計算
        cumsum = data.cumsum()
        running_max = cumsum.cummax()
        drawdown = (cumsum - running_max).min()

        pro_stats[p] = {
            "盈利效率": sharpe,
            "波動穩定度": std,
            "獲利偏度": sk,
            "最大回撤": drawdown,
            "單日最高": data.max()
        }

    df_pro = pd.DataFrame(pro_stats).T
    # 格式化顯示
    st.dataframe(
        df_pro.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=["盈利效率"]), 
        use_container_width=True
    )
    st.divider()

    # --- 2. 玩家五維屬性卡 (特大字體卡片) ---
    st.subheader("🛡️ 玩家五維屬性卡")
    
    attr_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        
        # 建立五維指標 (0-100 標格化)
        atk = min(100, int((data.max() / 500) * 100))        # 進攻: 最高得分
        dfs = max(0, int(100 - (abs(data.min()) / 500) * 100)) # 防守: 最低失分
        stb = max(0, int(100 - (data.std() / 300) * 100))    # 穩定: 標準差
        lck = int(((data.skew() or 0) + 2) / 4 * 100)        # 運氣: 偏度映射
        end = int((data > 0).sum() / len(df_master) * 100)   # 續航: 勝率
        
        with attr_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#ffffff; border:2px solid #eee; padding:15px; border-radius:20px; margin-bottom:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
                    <p style="margin:0; font-size:18px; color:#1f77b4; font-weight:900; text-align:center;">{p}</p>
                    <hr style="margin:8px 0;">
                    <div style="font-size:13px; color:#444; line-height:1.6;">
                        <b>🔥 進攻 (ATK):</b> {atk}<br>
                        <b>🛡️ 防守 (DFS):</b> {dfs}<br>
                        <b>⚖️ 穩定 (STB):</b> {stb}<br>
                        <b>🍀 運氣 (LCK):</b> {lck}<br>
                        <b>🔋 續航 (END):</b> {end}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 3. AI 賽博博弈建議 (大字體終端風格) ---
    st.subheader("🔮 AI 賽博預測建議")
    
    pred_cols = st.columns(2)
    for i, p in enumerate(players):
        data = df_master[p]
        # 計算最近一場嘅 Z-Score
        avg = data.mean()
        std = data.std()
        z_score = (data.iloc[-1] - avg) / std if std > 0 else 0
        
        # 戰略邏輯
        if z_score > 1.2:
            status, advice = "🔥 氣勢爆發", "當前手風極順，宜加碼進攻。"
        elif z_score < -1.2:
            status, advice = "❄️ 運勢低迷", "進入冷鋒期，建議改打防守牌。"
        else:
            status, advice = "🌀 均值回歸", "狀態平穩，維持目前節奏。"
            
        with pred_cols[i % 2]:
            st.markdown(f"""
                <div style="background-color:#1a1a1a; color:#00ff00; padding:15px; border-radius:15px; margin-bottom:15px; border: 1px solid #00ff00; font-family: monospace;">
                    <p style="margin:0; font-size:11px; color:#00cc00;">[SYS_MODEL]: {p.upper()}</p>
                    <p style="margin:5px 0; font-size:20px; font-weight:bold; color:#fff;">{status}</p>
                    <p style="margin:0; font-size:12px; line-height:1.4;">{advice}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- 4. 統計學備註 ---
    with st.expander("🔬 專業數據邏輯說明"):
        st.markdown("""
        * **獲利偏度 (Skewness)**: 
            * **正值**: 代表「爆發型」，靠少數幾場大贏撐起總分。
            * **負值**: 代表「穩健型」，但一旦輸球可能規模較大。
        * **盈利效率 (Sharpe)**: 衡量你在面對同等波動風險下，賺取積分的能力。
        * **五維屬性**: 根據歷史數據分布自動標格化 (Normalized) 得出的綜合戰力評分。
        """)
