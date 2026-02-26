import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money, get_connection
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    # 初始化選擇狀態 (Session State)
    if 'winner' not in st.session_state: st.session_state.winner = players[0]
    if 'loser' not in st.session_state: st.session_state.loser = players[1]

    # --- 1. 自動檢查並建立 Tab ---
    def ensure_today_tab():
        try:
            gc = get_connection()
            sh = gc.open_by_url(SHEET_URL)
            try:
                sh.worksheet(today_tab_name)
            except:
                new_ws = sh.add_worksheet(title=today_tab_name, rows="100", cols="10")
                new_ws.append_row(["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"])
                st.toast(f"✨ 已建立今日分頁: {today_tab_name}")
        except Exception as e:
            st.error(f"自動開 Tab 失敗: {e}")

    # --- 2. 今日累計 Summary ---
    df_today = pd.DataFrame()
    try:
        df_today = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
        if not df_today.empty:
            today_sums = df_today[players].sum()
            st.markdown("#### 📅 今日累計")
            cols = st.columns(4)
            for i, p in enumerate(players):
                val = today_sums[p]
                color = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
                cols[i].markdown(f"""
                    <div style="text-align:center; background-color:#f8f9fa; padding:8px 2px; border-radius:8px; border-bottom:4px solid {color};">
                        <p style="margin:0; font-size:12px; color:#666;">{p}</p>
                        <p style="margin:0; font-size:24px; font-weight:900; color:{color}; line-height:1.2;">{int(val):+d}</p>
                    </div>
                """, unsafe_allow_html=True)
    except:
        st.info("🐣 今日尚未有紀錄")

    st.divider()

    # --- 3. 錄入界面 (卡片式選擇器) ---

    # A. 誰贏了 (Winner Cards)
    st.markdown("🏆 **誰贏了？**")
    w_cols = st.columns(4)
    for i, p in enumerate(players):
        is_selected = (st.session_state.winner == p)
        btn_type = "primary" if is_selected else "secondary"
        if w_cols[i].button(p, key=f"win_{p}", use_container_width=True, type=btn_type):
            st.session_state.winner = p
            st.rerun()

    # B. 贏牌方式
    mode = st.radio("🎲 **方式**", ["出統", "自摸", "包自摸"], horizontal=True)
    
    # C. 誰付錢 (Loser Cards) - 只有非自摸才顯示
    loser = "三家"
    if mode in ["出統", "包自摸"]:
        st.markdown("💸 **誰付錢？**")
        l_cols = st.columns(4)
        potential_losers = [p for p in players if p != st.session_state.winner]
        
        # 如果原本選中的人變成了贏家，自動跳轉下一個輸家
        if st.session_state.loser == st.session_state.winner:
            st.session_state.loser = potential_losers[0]

        for p in players:
            if p == st.session_state.winner:
                l_cols[players.index(p)].button(p, key=f"lose_dis_{p}", use_container_width=True, disabled=True)
            else:
                is_selected = (st.session_state.loser == p)
                btn_type = "primary" if is_selected else "secondary"
                if l_cols[players.index(p)].button(p, key=f"lose_{p}", use_container_width=True, type=btn_type):
                    st.session_state.loser = p
                    st.rerun()
        loser = st.session_state.loser
        
    # D. 翻數
    fan = st.select_slider("🔥 **翻數**", options=list(range(3, 11)), value=3)
    
    # --- 分數計算 ---
    base = get_base_money(fan)
    res = {p: 0 for p in players}
    if mode == "出統":
        res[st.session_state.winner], res[loser] = base, -base
    elif mode == "包自摸":
        res[st.session_state.winner], res[loser] = base * 3, -(base * 3)
    else: # 自摸
        res[st.session_state.winner] = base * 3
        for p in players:
            if p != st.session_state.winner: res[p] = -base

    # --- 4. 變動預覽 (跟今日累計風格統一) ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with p_cols[i]:
            st.markdown(f"""
                <div style="background-color:{bg}; border-radius:10px; padding:10px 2px; text-align:center; min-height:65px; border:2px solid {txt if val != 0 else '#ccc'};">
                    <p style="margin:0; font-size:11px; font-weight:bold; color:#333;">{p}</p>
                    <p style="margin:2px 0 0 0; font-size:22px; font-weight:900; color:{txt};">{val:+d}</p>
                </div>
            """, unsafe_allow_html=True)

    st.write("") 

    if st.button("🚀 確認紀錄並上傳", width='stretch', type="primary"):
        with st.spinner('正在同步...'):
            ensure_today_tab()
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Remark": f"{st.session_state.winner} {mode} {fan}番"
            }
            new_entry.update(res)
            try:
                try:
                    df_curr = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
                    updated_df = pd.concat([df_curr, pd.DataFrame([new_entry])], ignore_index=True)
                except:
                    updated_df = pd.DataFrame([new_entry])
                
                conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                st.success(f"✅ 已存入 {today_tab_name}")
                st.rerun()
            except Exception as e:
                st.error(f"寫入失敗: {e}")

    st.divider()

    # --- 5. 管理數據 ---
    if not df_today.empty:
        st.markdown("#### ⚙️ 管理今日數據")
        with st.expander("📝 查看今日對局清單 / 撤銷", expanded=False):
            st.dataframe(df_today.copy().sort_index(ascending=False)[["Date"] + players], hide_index=True)
            if st.button("🗑️ 撤銷最後一局 (Undo)", width='stretch'):
                updated_df = df_today.drop(df_today.index[-1])
                conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                st.rerun()

        if st.button("🔄 同步至 Master Record (覆蓋)", width='stretch', type="secondary"):
            today_sums = df_today[players].sum()
            df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
            sync_entry = {"Date": today_tab_name, "Remark": f"Synced: {today_tab_name}"}
            sync_entry.update({p: today_sums[p] for p in players})
            if not df_master.empty:
                df_master['Date_str'] = df_master['Date'].astype(str)
                df_master = df_master[df_master['Date_str'] != today_tab_name]
                df_master = df_master.drop(columns=['Date_str'], errors='ignore')
            updated_master = pd.concat([df_master, pd.DataFrame([sync_entry])], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
            st.success("✅ 同步成功！")
