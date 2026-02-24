import streamlit as st
import pandas as pd

def show_history(df_master, players):
    st.header("📜 歷史紀錄與年度總結")
    
    if df_master.empty:
        st.warning("目前尚無歷史數據。")
        return

    # --- 1. 年度總結 (Yearly Summary) ---
    st.subheader("📅 年度戰績總計")
    
    # 複製一份數據來做處理，避免影響原始資料
    df_yearly = df_master.copy()
    df_yearly['Year'] = df_yearly['Date'].dt.year
    
    # 按年份加總
    yearly_summary = df_yearly.groupby('Year')[players].sum().sort_index(ascending=False)
    
    # 格式化年度總結表格
    st.dataframe(
        yearly_summary, 
        use_container_width=True,
        column_config={
            "Year": st.column_config.TextColumn("年份"),
            **{p: st.column_config.NumberColumn(f"{p} 總計", format="$%d") for p in players}
        }
    )

    st.divider()

    # --- 2. 詳細對局紀錄 (Detailed Logs) ---
    st.subheader("📝 每日對局明細")
    
    history_display = df_master.set_index("Date")[players].sort_index(ascending=False)
    # 將日期轉為字串格式
    history_display.index = history_display.index.strftime('%Y/%m/%d')
    
    st.dataframe(
        history_display, 
        use_container_width=True,
        column_config={
            **{p: st.column_config.NumberColumn(p, format="$%d") for p in players}
        }
    )

    # --- 3. 最近對局備註 (如果有 Remark 欄位) ---
    if 'Remark' in df_master.columns:
        st.divider()
        st.subheader("💬 最近對局摘要")
        recent_remarks = df_master[['Date', 'Remark']].sort_values(by='Date', ascending=False).head(10)
        recent_remarks['Date'] = recent_remarks['Date'].dt.strftime('%Y/%m/%d')
        st.table(recent_remarks.set_index('Date'))
