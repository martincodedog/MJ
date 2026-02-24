import streamlit as st
import pandas as pd
from datetime import datetime

def show_history(df_master, players):
    st.markdown("<h2 style='text-align: center;'>📜 歷史紀錄</h2>", unsafe_allow_html=True)
    
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # --- 1. 年度總結 ---
    st.subheader("📅 年度戰績總結")
    
    df_yearly = df_master.copy()
    df_yearly['Year'] = df_yearly['Date'].dt.year
    
    # 算各人年度總分
    yearly_summary = df_yearly.groupby('Year')[players].sum().sort_index(ascending=False)
    
    # 修正對局天數：計算該年度不重複日期
    yearly_days = df_yearly.groupby('Year')['Date'].apply(lambda x: x.dt.date.nunique())
    
    # 格式化：贏家加皇冠
    def add_winner_emoji_after(row):
        max_val = row.max()
        formatted = row.apply(lambda x: f"${x:,.0f}")
        if max_val > 0:
            max_idx = row.idxmax()
            formatted[max_idx] = f"{formatted[max_idx]} 👑"
        return formatted

    display_yearly = yearly_summary.apply(add_winner_emoji_after, axis=1)
    display_yearly['天數'] = yearly_days
    
    # 顯示年度表格
    st.dataframe(display_yearly, width='stretch')

    st.divider()

    # --- 2. 每日對局明細 (移除 Remark) ---
    st.subheader("📝 每日明細 (倒序)")
    
    history_display = df_master.copy().sort_values(by="Date", ascending=False)
    # iPhone 顯示精簡化：只留 月/日 時:分
    history_display['日期'] = history_display['Date'].dt.strftime('%m/%d %H:%M')
    
    # 只保留日期同玩家
    final_display = history_display[['日期'] + players].set_index("日期")
    
    st.dataframe(
        final_display,
        width='stretch',
        column_config={
            # 縮窄每一欄，確保 iPhone 直屏能顯示更多內容
            **{p: st.column_config.NumberColumn(p, width="small", format="$%d") for p in players}
        }
    )

    # --- 3. 年度之最 ---
    st.divider()
    current_year = datetime.now().year
    this_year_data = df_yearly[df_yearly['Year'] == current_year]
    
    if not this_year_data.empty:
        st.subheader(f"🏆 {current_year} 年度之最")
        c1, c2 = st.columns(2)
        with c1:
            big_winner = this_year_data[players].sum().idxmax()
            st.metric("年度金主", big_winner)
        with c2:
            max_single = this_year_data[players].max().max()
            lucky_guy = this_year_data[players].max().idxmax()
            st.metric("最強單局", lucky_guy, f"${max_single:,.0f}")
