import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("### 🧮 錄入對局 (自動分頁版)")
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # --- 1. 今日分數一覽 ---
    today_tab_name = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"#### 📅 今日戰況 ({today_tab_name})")
    
    try:
        # 嘗試讀取今日嘅 Tab
        df_today = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
        if not df_today.empty:
            # 只顯示分數欄位
            summary = df_today[players].sum().to_frame().T
            st.dataframe(summary, width='stretch', hide_index=True)
        else:
            st.info("今日暫時未有紀錄")
    except:
        st.info("🐣 今日第一場？紀錄後會自動開新 Tab")

    st.divider()

    # --- 2. 輸入區 ---
    col1, col2 = st.columns(2)
    with col1:
        winner = st.selectbox("🏆 贏家", players)
        fan = st.select_slider("🔥 翻數", options=list(range(3, 11)), value=3)
    with col2:
        mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
        if mode == "出統" or mode == "包自摸":
            loser = st.selectbox("💸 支付方", [p for p in players if p != winner])
        else:
            loser = "三家"

    base = get_base_money(fan)
    res = {p: 0 for p in players}
    
    # 計算邏輯
    if mode == "出統":
        res[winner], res[loser] = base, -base
    elif mode == "包自摸":
        res[winner], res[loser] = base * 3, -(base * 3)
    else:
        res[winner] = base * 3
        for p in players:
            if p != winner: res[p] = -base

    # --- 3. Entry Preview (寫入預覽) ---
    st.markdown("#### 📝 寫入預覽")
    preview_data = {
        "項目": ["時間", "變動", "備註"],
        "內容": [
            datetime.now().strftime("%H:%M"),
            ", ".join([f"{p}: {res[p]:+d}" for p in players if res[p] != 0]),
            f"{winner} {mode} {fan}番"
        ]
    }
    st.table(pd.DataFrame(preview_data))

    # --- 4. 執行紀錄 ---
    if st.button("🚀 確認紀錄 (同步至 Google Sheet)", width='stretch', type="primary"):
        with st.spinner('正在同步雲端...'):
            # 準備新數據
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Remark": f"{winner} {mode} {fan}番"
            }
            new_entry.update(res)
            new_df = pd.DataFrame([new_entry])

            # 嘗試寫入今日 Tab
            try:
                # 攞返今日 Tab 嘅舊數
                try:
                    existing_df = conn.read(spreadsheet=SHEET_URL, worksheet=today_tab_name, ttl=0)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                except:
                    # 如果 Tab 唔存在，就用 new_df 做開端
                    updated_df = new_df
                
                # 寫入今日 Tab
                conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                
                # 同步寫入總表 (Master Record) 供 Dashboard 使用
                master_df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
                master_updated = pd.concat([master_df, new_df], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=master_updated)
                
                st.success(f"✅ 紀錄成功！已同步至 Master 同今日 Tab ({today_tab_name})")
                import time
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 同步失敗: {e}")
