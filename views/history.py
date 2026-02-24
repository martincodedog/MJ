import streamlit as st

def show_history(df_master, players):
    st.header("📜 歷史得分紀錄")
    
    # 檢查數據是否為空
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # 1. 整理表格：將 Date 設為 Index 並格式化日期顯示
    # 我們只顯示玩家列
    history_display = df_master.set_index("Date")[players].sort_index(ascending=False)
    
    # 將日期索引轉為字串格式 YYYY/MM/DD
    history_display.index = history_display.index.strftime('%Y/%m/%d')
    
    # 2. 顯示表格
    st.dataframe(
        history_display, 
        use_container_width=True,
        column_config={
            "Date": st.column_config.TextColumn("日期"),
            # 可以為每個玩家加上格式化
            **{p: st.column_config.NumberColumn(p, format="$%d") for p in players}
        }
    )

    # 3. 額外的小功能：顯示最近五場的備註 (若有 Remark 欄位)
    if 'Remark' in df_master.columns:
        st.divider()
        st.subheader("📝 最近對局備註")
        recent_remarks = df_master[['Date', 'Remark']].sort_values(by='Date', ascending=False).head(10)
        recent_remarks['Date'] = recent_remarks['Date'].dt.strftime('%Y/%m/%d')
        st.table(recent_remarks.set_index('Date'))
