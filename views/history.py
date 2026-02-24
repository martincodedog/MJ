import streamlit as st
import pandas as pd

def show_history(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📜 歷史紀錄</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # --- 1. 年度總結 ---
    st.subheader("📅 年度戰績總結")
    
    df_yearly = df_master.copy()
    df_yearly['Year'] = df_yearly['Date'].dt.year
    
    # A. 算各人年度總分
    yearly_summary = df_yearly.groupby('Year')[players].sum().sort_index(ascending=False)
    
    # B. 修正對局天數：計算該年度有幾多個「不重複」日期
    # 注意：我哋攞 Date 嘅日期部分 (.dt.date) 再計 nunique
    yearly_days = df_yearly.groupby('Year')['Date'].apply(lambda x: x.dt.date.nunique())
    
    # C. 格式化：贏家加皇冠
    def add_winner_emoji_after(row):
        max_val = row.max()
        formatted = row.apply(lambda x: f"${x:,.0f}")
        if max_val > 0:
            max_idx = row.idxmax()
            formatted[max_idx] = f"{formatted[max_idx]} 👑"
        return formatted

    display_yearly = yearly_summary.apply(add_winner_emoji_after, axis=1)

    # --- 關鍵修正：確保 Index 對齊再合併 ---
    display_yearly['天數'] = yearly_days
    
    # iPhone 建議用 dataframe 方便左右滑動
    st.dataframe(display_yearly, width='stretch')

    st.divider()

    # --- 2. 每日對局明細 ---
    st.subheader("📝 每日明細 (倒序)")
    
    # 針對 iPhone 優化顯示內容
    history_display = df_master.copy().sort_values(by="Date", ascending=False)
    history_display['Date'] = history_display['Date'].dt.strftime('%m/%d %H:%M')
    
    # 只顯示 Date + 玩家 + Remark
    cols_to_show = ["Date"] + players
    if 'Remark' in history_display.columns:
        cols_to_show.append('Remark')
        
    st.dataframe(
        history_display[cols_to_show].set_index("Date"),
        width='stretch',
        column_config={
            **{p: st.column_config.NumberColumn(p, width="small", format="$%d") for p in players},
            "Remark": st.column_config.TextColumn("備註", width="medium")
        }
    )

    # --- 3. 年度小獎項 (iPhone 趣味版) ---
    st.divider()
    st.subheader("🏆 年度之最")
    current_year = datetime.now().year
    this_year_data = df_yearly[df_yearly['Year'] == current_year]
    
    if not this_year_data.empty:
        c1, c2 = st.columns(2)
        with c1:
            big_winner = this_year_data[players].sum().idxmax()
            st.metric("年度金主", big_winner, f"👑")
        with c2:
            # 搵出單場最高分
            max_single = this_year_data[players].max().max()
            lucky_guy = this_year_data[players].max().idxmax()
            st.metric("最強單局", lucky_guy, f"${max_single:,.0f}")
