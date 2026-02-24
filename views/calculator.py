import streamlit as st
from datetime import datetime
from utils import save_to_csv, get_base_money
import pandas as pd

def show_calculator_csv(players):
    st.markdown("### 🧮 錄入對局 (CSV Mode)")
    
    # Input Logic (Same as your optimized iPhone UI)
    winner = st.selectbox("🏆 贏家", players)
    mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
    
    if mode == "自摸":
        loser = "三家"
    else:
        loser = st.selectbox("💸 支付方", [p for p in players if p != winner])
        
    fan = st.select_slider("🔥 翻數", options=list(range(3, 11)), value=3)
    base = get_base_money(fan)

    # Calculation logic...
    res = {p: 0 for p in players}
    if mode == "出統":
        res[winner], res[loser] = base, -base
    elif mode == "包自摸":
        res[winner], res[loser] = base * 3, -(base * 3)
    else:
        res[winner] = base * 3
        for p in players:
            if p != winner: res[p] = -base

    # 在 views/calculator.py 錄入按鈕的部分
    if st.button("🚀 紀錄並存檔", use_container_width=True, type="primary"):
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            res["Martin"], res["Lok"], res["Stephen"], res["Fongka"],
            f"{winner} {mode} {fan}番"
        ]
        # 注意：這裡多傳入一個 players 參數
        save_to_csv(new_row, players) 
        st.success("數據已存入今日 CSV！")
        st.rerun()
