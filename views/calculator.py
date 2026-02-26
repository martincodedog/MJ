import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money, get_connection
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    
    # 初始化連線
    conn = st.connection("gsheets", type=GSheetsConnection)
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 自動檢查並建立 Tab (使用 gspread) ---
    def ensure_today_tab():
        try:
            gc = get_connection()
            sh = gc.open_by_url(SHEET_URL)
            try:
                sh.worksheet(today_tab_name)
            except:
                # 如果找不到，就開一個新 Tab 並加入 Header
                new_ws = sh.add_worksheet(title=today_tab_name, rows="100", cols="10")
                headers = ["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"]
                new_ws.append_row(headers)
                st.toast(f"✨ 已為你建立今日分頁: {today_tab_name}")
        except Exception as e:
            st.error(f"自動建立分頁失敗，請確保 Service Account 有權限: {e}")

    # --- 2. 顯示今日累計 Summary ---
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
                    <div style="text-align:center; background-color:#f8f9fa; padding:5px 2px; border-radius:8px; border-bottom:3px solid {color};">
                        <p style="margin:0; font-size:10px; color:#666;">{p}</p>
                        <p style="margin:0; font-size:14px; font-weight:bold; color:{color};">{int(val):+d}</p>
                    </div>
                """, unsafe_allow_html=True)

            # 同步至 Master Record
            st.write("")
            if st.button("🔄 同步今日總計至 Master Record", width='stretch'):
                with st.spinner('同步中...'):
                    df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
                    if not df_master.empty and today_tab_name in df_master['Date'].astype(str).values:
                        st.error(f"❌ {today_tab_name} 已經同步過了")
                    else:
                        sync_entry = {"Date": today_tab_name, "Remark": "Synced Total"}
                        sync_entry.update({p: today_sums[p] for p in players})
                        updated_master = pd.concat([df_master, pd.DataFrame([sync_entry])], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
                        st.success("✅ 已同步至總表")

            # 最後一局與刪除
            last_record = df_today.iloc[-1]
            with st.expander("⏮️ 查看今日最後一局 / 刪除", expanded=False):
                st.caption(f"{last_record['Remark']}")
                if st.button("🗑️ 刪除此局", width='stretch'):
                    updated_df = df_today.drop(df_today.index[-1])
                    conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                    st.rerun()
    except:
        st.info(f"🐣 今日尚未有紀錄，首筆提交將自動開 Tab")

    st.divider()

    # --- 3. 錄入界面 ---
    winner = st.selectbox("🏆 誰贏了？", players)
    mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
    loser = st.selectbox("💸 誰付錢？", [p for p in players if p != winner]) if mode != "自摸" else "三家"
    fan = st.select_slider("🔥 翻數", options=list(range(3, 11)), value=3)
    
    base = get_base_money(fan)
    res = {p: 0 for p in players}
    if mode == "出統":
        res[winner], res[loser] = base, -base
    elif mode == "包自摸":
        res[winner], res[loser] = base * 3, -(base * 3)
    else:
        res[winner] = base * 3
        for p in players:
            if p != winner: res[p] = -base

    # --- 4. 變動預覽 (全名) ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with p_cols[i]:
            st.markdown(f"""
                <div style="background-color:{bg}; border-radius:10px; padding:8px 2px; text-align:center; min-height:55px;">
                    <p style="margin:0; font-size:10px; font-weight:bold;">{p}</p>
                    <p style="margin:2px 0 0 0; font-size:15px; font-weight:900; color:{txt};">{val:+d}</p>
                </div>
            """, unsafe_allow_html=True)

    st.write("") 

    # --- 5. 提交按鈕 (觸發自動開 Tab) ---
    if st.button("🚀 確認紀錄並上傳", width='stretch', type="primary"):
        with st.spinner('正在同步...'):
            # 提交前先確保 Tab 存在
            ensure_today_tab()
            
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Remark": f"{winner} {mode} {fan}番"
            }
            new_entry.update(res)

            try:
                # 重新讀取今日 Tab 並寫入
                try:
                    df_curr = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
                    updated_df = pd.concat([df_curr, pd.DataFrame([new_entry])], ignore_index=True)
                except:
                    updated_df = pd.DataFrame([new_entry])
                
                conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                st.success(f"✅ 成功存入 {today_tab_name}")
                st.rerun()
            except Exception as e:
                st.error(f"寫入失敗: {e}")
