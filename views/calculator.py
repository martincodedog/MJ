import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # --- 1. 最後一局紀錄與今日戰況 ---
    today_tab_name = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # 同時讀取 Master Record 確保數據一致性
        df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
        
        if not df_master.empty:
            last_record = df_master.iloc[-1]
            
            # --- iPhone 專用最後紀錄卡片 ---
            with st.container():
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 12px; border: 1px solid #dcdfe6; margin-bottom: 20px;">
                    <p style="margin: 0; font-size: 12px; color: #666;">⏮️ 最後一局紀錄 ({last_record['Date'][-5:]})</p>
                    <p style="margin: 5px 0; font-size: 14px; font-weight: bold;">{last_record['Remark']}</p>
                    <div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 13px;">
                        <span>M: {int(last_record['Martin']):+d}</span>
                        <span>L: {int(last_record['Lok']):+d}</span>
                        <span>S: {int(last_record['Stephen']):+d}</span>
                        <span>F: {int(last_record['Fongka']):+d}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 刪除最後一筆按鈕 (危險動作使用紅色)
                if st.button("🗑️ 刪除最後一筆 (入錯數專用)", width='stretch'):
                    new_master = df_master.drop(df_master.index[-1])
                    conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=new_master)
                    st.warning("最後一筆紀錄已撤銷")
                    st.rerun()
    except Exception as e:
        st.info("尚未有對局紀錄")

    st.divider()

    # --- 2. 錄入界面 (iPhone 優化) ---
    # 使用大元件，方便手指點擊
    winner = st.selectbox("🏆 誰贏了？", players)
    
    mode = st.radio("🎲 贏牌方式", ["出統", "自摸", "包自摸"], horizontal=True)
    
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

    # --- 3. 實時動態預覽 ---
    # 在按按鈕前，直接顯示分數變化，視覺上非常 iPhone 化
    st.markdown("#### ⚡ 變動預覽")
    cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        color = "#28a745" if val > 0 else "#dc3545" if val < 0 else "#666"
        cols[i].markdown(f"<div style='text-align:center;'><b>{p[0]}</b><br><span style='color:{color}; font-weight:bold;'>{val:+d}</span></div>", unsafe_allow_html=True)

    st.write("") # 撐開空間

    # --- 4. 提交按鈕 ---
    if st.button("🚀 確認紀錄並上傳雲端", width='stretch', type="primary"):
        with st.spinner('正在同步中...'):
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Martin": res["Martin"],
                "Lok": res["Lok"],
                "Stephen": res["Stephen"],
                "Fongka": res["Fongka"],
                "Remark": f"{winner} {mode} {fan}番"
            }
            # 更新 Master Record
            master_df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
            # 確保欄位完全對齊
            new_row_df = pd.DataFrame([new_entry])[master_df.columns]
            updated_master = pd.concat([master_df, new_row_df], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
            
            st.success("紀錄成功！")
            st.rerun()
