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
    
    st.title(f"🧮 今日戰局: {today_date_str}")
    
    # --- 1. 即時累計計分板 ---
    with st.container(border=True):
        st.subheader("🏆 今日即時累計")
        try:
            sh = client.open_by_key(sheet_id)
            ws_today = sh.worksheet(sheet_tab_name)
            today_df = pd.DataFrame(ws_today.get_all_records())
            for p in players:
                today_df[p] = pd.to_numeric(today_df[p], errors='coerce').fillna(0)
        except:
            today_df = pd.DataFrame(columns=["Date"] + players + ["Remark"])

        m_cols = st.columns(4)
        for i, p in enumerate(players):
            day_val = today_df[p].sum() if p in today_df.columns else 0
            m_cols[i].metric(label=p, value=f"${day_val:,.0f}")

    st.divider()

    # --- 2. 錄入與預覽邏輯 (修正重點) ---
    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.subheader("📝 本局輸入")
        # 注意：我們不使用 st.form 包裹選擇器，這樣選擇改變時預覽才會即時變動
        winner = st.selectbox("🏆 贏家 (Winner)", players)
        mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
        
        # 動態顯示支付方
        if mode == "自摸":
            loser = "三家"
            st.info("自摸模式：其餘三家各付一份。")
        else:
            loser = st.selectbox("💸 支付方 (Loser)", [p for p in players if p != winner])
        
        fan = st.select_slider("🔥 翻數 (Fan)", options=list(range(3, 11)), value=3)
        base = get_base_money(fan)

    with col_right:
        st.subheader("🧐 數據預覽")
        
        # --- 核心計算邏輯修正 ---
        res = {p: 0 for p in players}
        
        if mode == "出統":
            # 贏家拿一份，輸家出一份
            res[winner] = base
            res[loser] = -base
        elif mode == "包自摸":
            # 輸家全包三份的錢
            res[winner] = base * 3
            res[loser] = -(base * 3)
        elif mode == "自摸":
            # 贏家拿三份，其餘三人各出一份
            res[winner] = base * 3
            for p in players:
                if p != winner:
                    res[p] = -base
        
        # 建立預覽表格
        preview_list = []
        for p in players:
            val = res[p]
            status = "👑 +" if val > 0 else "💸 " if val < 0 else "-"
            preview_list.append({"玩家": p, "預計損益": f"{status}${abs(val)}"})
        
        st.table(pd.DataFrame(preview_list).set_index("玩家"))
        
        # 錄入按鈕
        if st.button("🚀 確認錄入此局", use_container_width=True, type="primary"):
            ws_target = get_or_create_worksheet(client, sheet_id, sheet_tab_name)
            new_row = [
                datetime.now().strftime("%H:%M"), 
                res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], 
                f"{winner} {mode} {fan}番"
            ]
            ws_target.append_row(new_row)
            st.toast(f"✅ 已紀錄: {winner} +${res[winner]}", icon='🀄')
            st.rerun()

    # --- 3. 完場結算 ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🏁 完場結算 (同步至總表)"):
        if st.button("📤 執行結算並覆寫 Master", use_container_width=True):
            if not today_df.empty:
                ws_master = sh.worksheet(master_sheet_name)
                all_data = ws_master.get_all_values()
                rows_to_keep = [all_data[0]]
                for row in all_data[1:]:
                    if row[0] != today_date_str:
                        rows_to_keep.append(row)
                
                summary_row = [
                    today_date_str, 
                    int(today_df["Martin"].sum()), int(today_df["Lok"].sum()), 
                    int(today_df["Stephen"].sum()), int(today_df["Fongka"].sum()), 
                    f"Auto-Sync: {sheet_tab_name}"
                ]
                rows_to_keep.append(summary_row)
                ws_master.clear()
                ws_master.update('A1', rows_to_keep)
                st.success("🎊 結算成功！")
                st.cache_data.clear()
            else:
                st.error("今日尚無對局數據。")
