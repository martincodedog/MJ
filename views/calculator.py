import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # --- 1. 最後一局紀錄 (只顯示今日) ---
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # 讀取 Master Record
        df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
        
        if not df_master.empty:
            # 攞最後一行數據
            last_record = df_master.iloc[-1]
            last_date = last_record['Date'] # 假設格式係 "2026-02-24 16:00"
            
            # 檢查最後紀錄係咪今日發生
            if today_str in last_date:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 12px; border: 1px solid #dcdfe6; margin-bottom: 20px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">⏮️ 今日最後一局 ({last_date[-5:]})</p>
                        <p style="margin: 5px 0; font-size: 14px; font-weight: bold;">{last_record['Remark']}</p>
                        <div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 13px;">
                            <span>M: {int(last_record['Martin']):+d}</span>
                            <span>L: {int(last_record['Lok']):+d}</span>
                            <span>S: {int(last_record['Stephen']):+d}</span>
                            <span>F: {int(last_record['Fongka']):+d}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️ 刪除今日最後一筆", width='stretch'):
                        new_master = df_master.drop(df_master.index[-1])
                        conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=new_master)
                        st.warning("最後一筆紀錄已撤銷")
                        st.rerun()
            else:
                # 如果唔係今日，可以顯示一個簡單提示或者乾脆空白
                st.caption("ℹ️ 今日暫時未有對局紀錄")
    except Exception as e:
        # 預防萬一讀取失敗
        pass

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

    # --- 3. ⚡ 變動預覽 UI 強化版 ---
    st.markdown("#### ⚡ 變動預覽")
    
    # 用一個 Container 框住預覽區，增加視覺一致性
    with st.container():
        # 建立四行，iPhone 上面每行顯示一個玩家
        cols = st.columns(4)
        
        for i, p in enumerate(players):
            val = res[p]
            
            # 根據贏輸決定顏色同背景
            if val > 0:
                bg_color = "#e6f4ea"  # 淺綠背景
                text_color = "#1e8e3e" # 深綠字
                border_color = "#1e8e3e"
                symbol = "+"
            elif val < 0:
                bg_color = "#fce8e6"  # 淺紅背景
                text_color = "#d93025" # 深紅字
                border_color = "#d93025"
                symbol = ""
            else:
                bg_color = "#f1f3f4"  # 灰色背景
                text_color = "#5f6368" # 灰色字
                border_color = "#bdc1c6"
                symbol = ""

            # 注入自定義 HTML 卡片
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    padding: 8px 5px;
                    text-align: center;
                ">
                    <p style="margin: 0; font-size: 12px; color: #555; font-weight: bold;">{p[0]}</p>
                    <p style="margin: 0; font-size: 16px; font-weight: 900; color: {text_color};">
                        {symbol}{val}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    st.write("") # 增加與按鈕之間的間距

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
