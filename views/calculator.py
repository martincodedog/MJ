import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 獲取今日日期字串
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        # 讀取 Master Record
        df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
        
        if not df_master.empty:
            # --- 1. 新增：今日 Summary 區域 ---
            # 篩選今日數據 (確保 Date 欄位包含今日日期)
            df_today = df_master[df_master['Date'].str.contains(today_str, na=False)]
            
            if not df_today.empty:
                # 計算今日各人總分
                today_sums = df_today[players].sum()
                
                st.markdown("#### 📅 今日累計")
                # iPhone 專用橫向小卡片 Summary
                cols = st.columns(4)
                for i, p in enumerate(players):
                    val = today_sums[p]
                    color = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
                    cols[i].markdown(f"""
                        <div style="text-align:center; background-color:#f8f9fa; padding:5px; border-radius:8px; border-bottom:3px solid {color};">
                            <p style="margin:0; font-size:11px; color:#666;">{p[0]}</p>
                            <p style="margin:0; font-size:15px; font-weight:bold; color:{color};">{int(val):+d}</p>
                        </div>
                    """, unsafe_allow_html=True)
                st.write("") # 留白
            
            # --- 2. 原有的最後一局紀錄 (僅今日) ---
            last_record = df_master.iloc[-1]
            if today_str in last_record['Date']:
                with st.expander("⏮️ 查看上一局明細", expanded=False):
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; font-size: 13px;">
                        <p style="margin: 0; font-weight: bold;">{last_record['Remark']}</p>
                        <p style="margin: 5px 0 0 0; font-family: monospace;">
                            M:{int(last_record['Martin']):+d} L:{int(last_record['Lok']):+d} S:{int(last_record['Stephen']):+d} F:{int(last_record['Fongka']):+d}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ 刪除最後一筆", width='stretch'):
                        new_master = df_master.drop(df_master.index[-1])
                        conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=new_master)
                        st.warning("已刪除")
                        st.rerun()

    except Exception as e:
        st.caption("暫無今日紀錄")

    st.divider()

    # --- 3. 錄入界面 ---
    winner = st.selectbox("🏆 誰贏了？", players)
    mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
    
    if mode in ["出統", "包自摸"]:
        loser = st.selectbox("💸 誰付錢？", [p for p in players if p != winner])
    else:
        loser = "三家"
        
    fan = st.select_slider("🔥 翻數", options=list(range(3, 11)), value=3)
    
    # 計算分數
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

    # --- 4. 變動預覽 UI (之前優化過嘅部分) ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with p_cols[i]:
            st.markdown(f"""
                <div style="background-color:{bg}; border-radius:10px; padding:8px 5px; text-align:center;">
                    <p style="margin:0; font-size:12px; font-weight:bold;">{p[0]}</p>
                    <p style="margin:0; font-size:16px; font-weight:900; color:{txt};">{val:+d}</p>
                </div>
            """, unsafe_allow_html=True)

    st.write("") 

    if st.button("🚀 確認紀錄並上傳", width='stretch', type="primary"):
        with st.spinner('同步中...'):
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Martin": res["Martin"], "Lok": res["Lok"], "Stephen": res["Stephen"], "Fongka": res["Fongka"],
                "Remark": f"{winner} {mode} {fan}番"
            }
            master_df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
            new_row_df = pd.DataFrame([new_entry])[master_df.columns]
            updated_master = pd.concat([master_df, new_row_df], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
            st.success("紀錄成功！")
            st.rerun()
