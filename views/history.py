import streamlit as st
import pandas as pd

def show_history(df_master, players):
    st.header("📜 歷史紀錄與年度總結")
    
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # --- 1. 年度總結 (Yearly Summary) ---
    st.subheader("📅 年度戰績總結 (年度最強)")
    
    df_yearly = df_master.copy()
    df_yearly['Year'] = df_yearly['Date'].dt.year
    
    # 算出年度總計數字與對局天數
    yearly_summary = df_yearly.groupby('Year')[players].sum().sort_index(ascending=False)
    yearly_days = df_yearly.groupby('Year')['Date'].count()
    
    # 定義格式化邏輯：每行最高分（Winner）在數字後加 👑
    def add_winner_emoji_after(row):
        # 找出最大值的玩家名
        max_idx = row.idxmax()
        
        # 轉換為字串格式
        formatted = row.apply(lambda x: f"${x:,.0f}")
        
        # 只有當最高分大於 0 時，在數字後加皇冠
        if row[max_idx] > 0:
            formatted[max_idx] = f"{formatted[max_idx]} 👑"
            
        return formatted

    # 應用格式化
    display_yearly = yearly_summary.apply(add_winner_emoji_after, axis=1)

    # 在表格中加入對局天數資訊
    display_yearly['對局天數'] = yearly_days.values

    # 顯示年度表格
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

    # --- 3. 最近備註 (如有 Remark 欄位) ---
    if 'Remark' in df_master.columns:
        st.divider()
        st.subheader("💬 最近對局摘要")
        recent_remarks = df_master[['Date', 'Remark']].sort_values(by='Date', ascending=False).head(10)
        recent_remarks['Date'] = recent_remarks['Date'].dt.strftime('%Y/%m/%d')
        st.table(recent_remarks.set_index('Date'))
