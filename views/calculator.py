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
    
    # --- UI Header ---
    st.title(f"🧮 今日戰局: {today_date_str}")
    
    # 1. LIVE STANDINGS CARD
    with st.container(border=True):
        st.subheader("🏆 今日即時累計 (Live Score)")
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
            # Color logic: Green for winning today, Red for losing
            color = "normal" if day_val == 0 else "normal"
            m_cols[i].metric(label=f"👤 {p}", value=f"${day_val:,.0f}")
    
    st.markdown("---")

    # 2. INPUT & PREVIEW SECTION
    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.subheader("📝 本局錄入")
        with st.form("mahjong_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                winner = st.selectbox("🏆 贏家 (Winner)", players)
                fan = st.select_slider("🔥 翻數 (Fan)", options=list(range(3, 11)), value=3)
            with c2:
                mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=False)
                loser = st.selectbox("💸 支付方", [p for p in players if p != winner]) if mode != "自摸" else "三家"
            
            base = get_base_money(fan)
            submit_btn = st.form_submit_button("🚀 確認錄入此局", use_container_width=True)

    with col_right:
        st.subheader("🧐 數據預覽 (Preview)")
        res = {p: 0 for p in players}
        if mode == "出統": 
            res[winner], res[loser] = base, -base
        elif mode == "包自摸": 
            res[winner], res[loser] = base * 3, -(base * 3)
        else: 
            res[winner] = base * 3
            for p in players: 
                if p != winner: res[p] = -base
        
        # Fancy Preview Table
        preview_data = []
        for p in players:
            val = res[p]
            status = "🏆 +" if val > 0 else "💸" if val < 0 else "-"
            preview_data.append({"玩家": p, "預計損益": f"{status} ${abs(val)}"})
        
        st.table(pd.DataFrame(preview_data).set_index("玩家"))
        st.caption(f"備註: {winner} {mode} {fan}番")

    # 3. FORM SUBMISSION LOGIC
    if submit_btn:
        ws_target = get_or_create_worksheet(client, sheet_id, sheet_tab_name)
        new_row = [
            datetime.now().strftime("%Y/%m/%d %H:%M"), 
            res["Martin"], res["Lok"], res["Stephen"], res["Fongka"], 
            f"{winner} {mode} {fan}番"
        ]
        ws_target.append_row(new_row)
        st.toast(f"✅ 已紀錄: {winner} +${res[winner]}", icon='🀄')
        st.rerun()

    # 4. SETTLEMENT SECTION (Visual Separation)
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🏁 完場結算 (Danger Zone)"):
        st.warning("結算後將會覆寫 Master Record 內的今日總分。")
        if st.button("📤 同步至總表", type="primary", use_container_width=True):
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
                    f"Sync: {sheet_tab_name}"
                ]
                rows_to_keep.append(summary_row)
                ws_master.clear()
                ws_master.update('A1', rows_to_keep)
                st.success("🎊 結算成功！Master Record 已更新。")
                st.cache_data.clear()
            else:
                st.error("今日暫無數據。")
