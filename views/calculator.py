import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money, get_connection
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    # 初始化選擇狀態
    if 'winner' not in st.session_state: st.session_state.winner = players[0]
    if 'loser' not in st.session_state: st.session_state.loser = players[1]

    # --- 1. 自動檢查並建立 Tab (新增欄位定義) ---
    def ensure_today_tab():
        try:
            gc = get_connection()
            sh = gc.open_by_url(SHEET_URL)
            try:
                sh.worksheet(today_tab_name)
            except:
                # 定義標題列：日期, 玩家1~4, 贏家, 輸家, 方式, 番數, 備註
                header = ["Date"] + players + ["Winner", "Loser", "Method", "Fan", "Remark"]
                new_ws = sh.add_worksheet(title=today_tab_name, rows="500", cols="15")
                new_ws.append_row(header)
                st.toast(f"✨ 已建立今日分頁: {today_tab_name}")
        except Exception as e:
            st.error(f"自動開 Tab 失敗: {e}")

    # --- 2. 今日累計 Summary (保持原樣) ---
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

    # --- 3. 錄入界面 ---
    st.markdown("🏆 **誰贏了？**")
    w_cols = st.columns(4)
    for i, p in enumerate(players):
        is_selected = (st.session_state.winner == p)
        if w_cols[i].button(p, key=f"win_{p}", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.winner = p
            st.rerun()

    mode = st.radio("🎲 **方式**", ["出統", "自摸", "包自摸"], horizontal=True)
    
    loser_display = "三家"
    if mode in ["出統", "包自摸"]:
        st.markdown(f"💸 **誰{'付錢' if mode=='出統' else '包牌'}？**")
        l_cols = st.columns(4)
        if st.session_state.loser == st.session_state.winner:
            st.session_state.loser = [p for p in players if p != st.session_state.winner][0]

        for p in players:
            if p == st.session_state.winner:
                l_cols[players.index(p)].button(p, key=f"lose_dis_{p}", use_container_width=True, disabled=True)
            else:
                is_selected = (st.session_state.loser == p)
                if l_cols[players.index(p)].button(p, key=f"lose_{p}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    st.session_state.loser = p
                    st.rerun()
        loser_display = st.session_state.loser
        
    fan = st.select_slider("🔥 **翻數**", options=list(range(3, 14)), value=3)
    
    # 計算得分邏輯
    base = get_base_money(fan)
    res = {p: 0 for p in players}
    if mode == "出統":
        res[st.session_state.winner], res[st.session_state.loser] = base, -base
    elif mode == "包自摸":
        res[st.session_state.winner], res[st.session_state.loser] = base * 3, -(base * 3)
    else: # 自摸
        res[st.session_state.winner] = base * 3
        for p in players:
            if p != st.session_state.winner: res[p] = -base

    # --- 4. 變動預覽 ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        p_cols[i].markdown(f"""
            <div style="background-color:{bg}; border-radius:10px; padding:10px 2px; text-align:center; border:2px solid {txt if val != 0 else '#ccc'};">
                <p style="margin:0; font-size:11px; font-weight:bold; color:#333;">{p}</p>
                <p style="margin:2px 0 0 0; font-size:22px; font-weight:900; color:{txt};">{val:+d}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 5. 確認上傳 (新增欄位寫入) ---
    if st.button("🚀 確認紀錄並上傳", use_container_width=True, type="primary"):
        with st.spinner('正在同步...'):
            ensure_today_tab()
            
            # 建立結構化數據
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Winner": st.session_state.winner,
                "Loser": loser_display,
                "Method": mode,
                "Fan": fan,
                "Remark": f"{st.session_state.winner} {mode} {fan}番"
            }
            new_entry.update(res) # 合併玩家分數
            
            try:
                # 讀取現有數據並合併
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
