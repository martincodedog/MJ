import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    try:
        # 讀取今日專屬 Tab
        df_today = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
        
        if not df_today.empty:
            # --- 1. 今日 Summary ---
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

            # --- 2. 同步到 Master Record 按鈕 ---
            st.write("")
            if st.button("🔄 同步今日總計至 Master Record", width='stretch', type="secondary"):
                with st.spinner('正在同步至總表...'):
                    # 讀取 Master Record
                    df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
                    
                    # 檢查是否今日已經同步過 (防止重複同步)
                    if not df_master.empty and today_tab_name in df_master['Date'].values:
                        st.error(f"❌ {today_tab_name} 的數據已經同步過了！")
                    else:
                        # 準備同步數據 (將今日加總變為一筆紀錄)
                        sync_entry = {
                            "Date": today_tab_name,
                            "Martin": today_sums["Martin"],
                            "Lok": today_sums["Lok"],
                            "Stephen": today_sums["Stephen"],
                            "Fongka": today_sums["Fongka"],
                            "Remark": f"Synced: {today_tab_name} 總計"
                        }
                        
                        # 合併並更新
                        updated_master = pd.concat([df_master, pd.DataFrame([sync_entry])], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
                        st.success(f"✅ 已成功將今日總計同步至 Master Record！")
            
            # --- 3. 今日最後一局 ---
            last_record = df_today.iloc[-1]
            with st.expander("⏮️ 查看今日上一局 / 刪除", expanded=False):
                st.markdown(f"<p style='font-size:13px;'>{last_record['Remark']}</p>", unsafe_allow_html=True)
                if st.button("🗑️ 刪除此局", width='stretch'):
                    updated_df = df_today.drop(df_today.index[-1])
                    conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                    st.warning("已刪除")
                    st.rerun()

    except Exception:
        st.info(f"🐣 今日尚未有紀錄 ({today_tab_name})")

    st.divider()

    # --- 4. 錄入界面 ---
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

    # --- 5. 變動預覽 ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with p_cols[i]:
            st.markdown(f"<div style='background-color:{bg}; border-radius:10px; padding:8px 2px; text-align:center;'><b>{p}</b><br><span style='font-size:15px; font-weight:900; color:{txt};'>{val:+d}</span></div>", unsafe_allow_html=True)

    # --- 6. 提交至今日 Tab ---
    if st.button("🚀 確認紀錄 (存入今日 Tab)", width='stretch', type="primary"):
        with st.spinner('同步中...'):
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Martin": res["Martin"], "Lok": res["Lok"], "Stephen": res["Stephen"], "Fongka": res["Fongka"],
                "Remark": f"{winner} {mode} {fan}番"
            }
            try:
                try:
                    df_current = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
                    updated_df = pd.concat([df_current, pd.DataFrame([new_entry])], ignore_index=True)
                except:
                    updated_df = pd.DataFrame([new_entry])
                
                conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                st.success(f"✅ 已存入 {today_tab_name}")
                st.rerun()
            except Exception as e:
                st.error(f"失敗: {e}")
