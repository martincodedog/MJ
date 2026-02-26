import streamlit as st
import pandas as pd

def show_pro_analysis(df_master, players):
    st.markdown("<h2 style='text-align: center;'>🧠 Gemini 雀神進階建模</h2>", unsafe_allow_html=True)
    
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

    # --- 3. Gemini 深度雀評 (約 500 字地道點評) ---
    st.divider()
    st.subheader("🔮 Gemini 賽博戰報 (Deep Analysis)")
    
    last_day = df_master.iloc[-1]
    winner = last_day[players].idxmax()
    loser = last_day[players].idxmin()
    win_val = int(last_day[winner])
    loss_val = int(last_day[loser])

    st.markdown(f"""
    <div style="background-color:#0e1117; color:#FAFAFA; padding:30px; border-radius:24px; border: 1px solid #4285F4; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
        <div style="display:flex; align-items:center; margin-bottom:20px;">
            <div style="width:15px; height:15px; background-color:#4285F4; border-radius:50%; margin-right:12px; box-shadow:0 0 10px #4285F4;"></div>
            <span style="font-size:20px; font-weight:bold; color:#4285F4; letter-spacing:1px;">GEMINI DEEP ANALYSIS v3.1</span>
        </div>
        
        <div style="font-size:17px; line-height:1.9; font-family: 'Inter', sans-serif;">
            <p>各位雀友，請坐低。我係 <b>Gemini</b>。讀取完今日份數據之後，我嘅後台處理器差點過熱——唔係因為運算太複雜，而係因為今日嘅對局結果實在太過「荒謬」。</p>
            
            <p>首先，我哋要用「國家級」嘅規格嚟賀一賀 <b>{winner}</b>。贏咗 <b>{win_val}</b> 分？呢個數字已經唔係單純嘅「手風順」，呢個直情係「物理規律嘅崩壞」。我強烈懷疑你今日係咪去咗轉運、或者你件衫入面收埋咗成打「白板」。你每一場嘅自摸機率都高到唔合理，我建議其餘三位檢查下 <b>{winner}</b> 張凳底，睇下係咪裝咗強力吸金磁鐵。贏到咁盡，你今晚唔請大家食餐龍蝦、再加個鮑魚撈飯，我驚你聽日出街會俾人喺後面指指點點，話你係雀壇嘅「冷血屠夫」。</p>
            
            <p>至於 <b>{loser}</b> 方面... 我真心想為你降半旗。輸咗 <b>{loss_val}</b> 分，你今日個角色好鮮明，就係<b>「雀壇慈善傳奇」</b>。每次你打出一隻牌，我就聽到你荷包入面啲銀紙喺度唱《祝君好》。你今日係咪專門嚟派錢？定係你同大家簽咗咩「積分無償讓渡協議」？你今日出銃嘅次數，已經多到連我呢個 AI 都數唔過嚟。聽我 Gemini 一句勸：下次見到 <b>{winner}</b> 坐你對家，你就話肚痛唔好打，或者直接將錢擺喺枱面然後走咗去，起碼可以慳返啲體力，留返嚟下次再派。</p>
            
            <p>總結今日對局，簡直係一場「單方面嘅社會實驗」。有人贏到笑，有人輸到跳。香港麻雀講求「技術、心理、手風」，但我喺你哋身上淨係睇到「亂打、衝動、同埋對命運嘅絕望」。<b>{', '.join(players)}</b>，希望下次開枱，大家可以帶返個腦上枱，唔好再將麻雀枱變成大型慈善籌款現場。</p>
            
            <p style="color:#4285F4; font-weight:bold; margin-top:25px; border-left:4px solid #4285F4; padding-left:15px;">
            >>> [SYSTEM_MESSAGE]: 分析完畢。建議：贏家低調啲，輸家去拜神。
            </p>
        </div>
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
