import streamlit as st
import pandas as pd

def show_history(df_master, players):
    st.header("📜 歷史紀錄與年度總結")
    
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # --- 1. 年度總結 (Yearly Summary) ---
    st.subheader("📅 年度戰績總計")
    
    df_yearly = df_master.copy()
    df_yearly['Year'] = df_yearly['Date'].dt.year
    
    # 算出年度總計數字
    yearly_summary = df_yearly.groupby('Year')[players].sum().sort_index(ascending=False)
    
    # 定義 Emoji 邏輯：每行最高分加 👑，最低分加 💸
    def add_summary_emojis(row):
        # 找出最大值和最小值的索引
        max_idx = row.idxmax()
        min_idx = row.idxmin()
        
        # 轉換為字串並加入格式
        formatted = row.apply(lambda x: f"${x:,.0f}")
        
        # 如果有正分才加皇冠，有負分才加錢包 (避免大家平手時亂加)
        if row[max_idx] > 0:
            formatted[max_idx] = f"👑 {formatted[max_idx]}"
        if row[min_idx] < 0:
            formatted[min_idx] = f"💸 {formatted[min_idx]}"
            
        return formatted

    # 應用格式化
    display_yearly = yearly_summary.apply(add_summary_emojis, axis=1)

    # 顯示年度表格 (使用 st.table 確保 Emoji 完整顯示)
    st.table(display_yearly)

    st.divider()

    # --- 2. 每日對局明細 ---
    st.subheader("📝 每日對局明細")
    
    history_display = df_master.set_index("Date")[players].sort_index(ascending=False)
    history_display.index = history_display.index.strftime('%Y/%m/%d')
    
    st.dataframe(
        history_display, 
        use_container_width=True,
        column_config={
            **{p: st.column_config.NumberColumn(p, format="$%d") for p in players}
        }
    )

    # --- 3. 最近備註 ---
    if 'Remark' in df_master.columns:
        st.divider()
        st.subheader("💬 最近對局摘要")
        recent_remarks = df_master[['Date', 'Remark']].sort_values(by='Date', ascending=False).head(10)
        recent_remarks['Date'] = recent_remarks['Date'].dt.strftime('%Y/%m/%d')
        st.table(recent_remarks.set_index('Date'))
