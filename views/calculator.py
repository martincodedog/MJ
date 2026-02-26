import streamlit as st
from datetime import datetime
import pandas as pd
from utils import SHEET_URL, get_base_money, get_connection
from streamlit_gsheets import GSheetsConnection

def show_calculator(players):
    st.markdown("<h2 style='text-align: center;'>🧮 快速計分</h2>", unsafe_allow_html=True)
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    today_tab_name = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 自動檢查並建立 Tab 邏輯 ---
    def ensure_today_tab():
        try:
            gc = get_connection()
            sh = gc.open_by_url(SHEET_URL)
            try:
                sh.worksheet(today_tab_name)
            except:
                new_ws = sh.add_worksheet(title=today_tab_name, rows="100", cols="10")
                headers = ["Date", "Martin", "Lok", "Stephen", "Fongka", "Remark"]
                new_ws.append_row(headers)
                st.toast(f"✨ 已建立今日分頁: {today_tab_name}")
        except Exception as e:
            st.error(f"自動開 Tab 失敗: {e}")

    # --- 2. 顯示今日累計 Summary (字體放大) ---
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
                        <p style="margin:0; font-size:22px; font-weight:900; color:{color}; line-height:1.2;">{int(val):+d}</p>
                    </div>
                """, unsafe_allow_html=True)

            # --- 3. 同步至 Master Record (Overwrite 邏輯) ---
            st.write("")
            if st.button("🔄 同步今日總計至總表 (覆蓋)", width='stretch', type="secondary"):
                with st.spinner('正在更新 Master Record...'):
                    df_master = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
                    
                    sync_entry = {"Date": today_tab_name, "Remark": f"Synced: {today_tab_name}"}
                    sync_entry.update({p: today_sums[p] for p in players})
                    
                    # 檢查並覆蓋：過濾掉日期相同的舊紀錄
                    if not df_master.empty:
                        # 確保 Date 欄位是字串進行比對
                        df_master['Date_str'] = df_master['Date'].astype(str)
                        if today_tab_name in df_master['Date_str'].values:
                            st.info("🔄 發現舊紀錄，正在覆蓋...")
                            df_master = df_master[df_master['Date_str'] != today_tab_name]
                        
                        df_master = df_master.drop(columns=['Date_str'], errors='ignore')
                    
                    updated_master = pd.concat([df_master, pd.DataFrame([sync_entry])], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_master)
                    st.success(f"✅ {today_tab_name} 數據已同步/更新！")

            # --- 4. 查看今日所有紀錄 / 刪除 ---
            with st.expander("📝 查看今日對局清單", expanded=False):
                # 整理顯示用的 DataFrame
                display_df = df_today.copy()
                display_df = display_df.sort_index(ascending=False) # 倒序，最新在上面
                st.dataframe(
                    display_df[["Date"] + players], 
                    hide_index=True,
                    column_config={p: st.column_config.NumberColumn(p, format="$%d") for p in players}
                )
                
                if st.button("🗑️ 刪除最後一局 (Undo)", width='stretch'):
                    updated_df = df_today.drop(df_today.index[-1])
                    conn.update(spreadsheet=SHEET_URL, worksheet=today_tab_name, data=updated_df)
                    st.warning("最後一筆已刪除")
                    st.rerun()
    except:
        st.info(f"🐣 今日尚未有紀錄 ({today_tab_name})")

    st.divider()

    # --- 5. 錄入界面 ---
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

    # --- 6. 變動預覽 ---
    st.markdown("#### ⚡ 變動預覽")
    p_cols = st.columns(4)
    for i, p in enumerate(players):
        val = res[p]
        bg = "#e6f4ea" if val > 0 else "#fce8e6" if val < 0 else "#f1f3f4"
        txt = "#1e8e3e" if val > 0 else "#d93025" if val < 0 else "#5f6368"
        with p_cols[i]:
            st.markdown(f"""
                <div style="background-color:{bg}; border-radius:10px; padding:8px 2px; text-align:center; min-height:60px;">
                    <p style="margin:0; font-size:11px; font-weight:bold;">{p}</p>
                    <p style="margin:2px 0 0 0; font-size:18px; font-weight:900; color:{txt};">{val:+d}</p>
                </div>
            """, unsafe_allow_html=True)

    st.write("") 

    if st.button("🚀 確認紀錄並上傳", width='stretch', type="primary"):
        with st.spinner('正在同步...'):
            ensure_today_tab()
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Remark": f"{winner} {mode} {fan}番"
            }
            new_entry.update(res)
            try:
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
