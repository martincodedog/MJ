import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_base_money

def get_or_create_worksheet(client, sheet_id, sheet_name):
    sh = client.open_by_key(sheet_id)
    try:
        return sh.worksheet(sheet_name)
    except:
        new_ws = sh.add_worksheet(title=sheet_name, rows="100", cols="10")
        new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
        return new_ws

def show_calculator(client, sheet_id, master_sheet_name, players):
    today_date_str = datetime.now().strftime("%Y/%m/%d")
    sheet_tab_name = today_date_str.replace("/", "-")
    
    st.header(f"🧮 今日對局錄入: {today_date_str}")

    # 1. Fetch Today's Data
    try:
        sh = client.open_by_key(sheet_id)
        ws_today = sh.worksheet(sheet_tab_name)
        today_df = pd.DataFrame(ws_today.get_all_records())
        for p in players:
            today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
    except:
        today_df = pd.DataFrame(columns=["Date"] + players + ["Remark"])

    # 2. Today's Summary (The "Big Numbers")
    st.markdown("### 🏆 今日即時累積")
    m_cols = st.columns(4)
    for i, p in enumerate(players):
        day_val = today_df[p].sum() if p in today_df.columns else 0
        m_cols[i].metric(label=p, value=f"${day_val:,.0f}")

    st.divider()

    # 3. Entry Form
    col_in, col_pre = st.columns([1, 1])
    with col_in:
        st.markdown("#### 📝 錄入數據")
        winner = st.selectbox("贏家", players)
        mode = st.radio("方式", ["出統", "自摸", "包自摸"], horizontal=True)
        loser = st.selectbox("誰支付？", [p for p in players if p != winner]) if mode != "自摸" else "三家"
        fan = st.select_slider("翻數", options=list(range(3, 11)), value=3)
        base = get_base_money(fan)

    with col_pre:
        st.markdown("#### 🧐 預覽寫入內容")
        res = {p: 0 for p in players}
        if mode == "出統": res[winner], res[loser] = base, -base
        elif mode == "包自摸": res[winner], res[loser] = base * 3, -(base * 3)
        else: 
            res[winner] = base * 3
            for p in players: 
                if p != winner: res[p] = -base
        
        preview_row = {**{p: [res[p]] for p in players}, "備註": [f"{winner} {mode} {fan}番"]}
        st.table(pd.DataFrame(preview_row))

    if st.button("🚀 確認錄入此局", use_container_width=True):
        ws_target = get_or_create_worksheet(client, sheet_id, sheet_tab_name)
        new_row = [
            datetime.now().strftime("%Y/%m/%d %H:%M"), 
            res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], 
            f"{winner} {mode} {fan}番"
        ]
        ws_target.append_row(new_row)
        st.success("✅ 數據已寫入今日分頁")
        st.rerun()

    # 4. Final Sync / Overwrite logic
    st.divider()
    st.markdown("### 🏁 完場結算")
    if st.button("📤 結算並覆寫 Master Record", type="primary", use_container_width=True):
        if not today_df.empty:
            ws_master = sh.worksheet(master_sheet_name)
            all_data = ws_master.get_all_values()
            
            # Filter out existing entries for today
            rows_to_keep = [all_data[0]] # Keep headers
            for row in all_data[1:]:
                if row[0] != today_date_str:
                    rows_to_keep.append(row)
            
            # Add new summary
            summary_row = [
                today_date_str, 
                int(today_df["Martin"].sum()), 
                int(today_df["Lok"].sum()), 
                int(today_df["Stephen"].sum()), 
                int(today_df["Fongka"].sum()), 
                f"Sync: {sheet_tab_name}"
            ]
            rows_to_keep.append(summary_row)
            
            ws_master.clear()
            ws_master.update('A1', rows_to_keep)
            st.success("🎊 總表結算完成！")
            st.cache_data.clear()
        else:
            st.error("今日暫無數據。")
