import streamlit as st
from datetime import datetime
from utils import save_to_gsheet, get_base_money

def show_calculator(players):
    st.markdown("### 🧮 錄入對局 (雲端同步)")
    
    winner = st.selectbox("🏆 贏家", players)
    mode = st.radio("🎲 方式", ["出統", "自摸", "包自摸"], horizontal=True)
    
    if mode == "自摸":
        loser = "三家"
    else:
        loser = st.selectbox("💸 支付方", [p for p in players if p != winner])
        
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

    if st.button("🚀 紀錄並同步到雲端", width='stretch', type="primary"):
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            res["Martin"], res["Lok"], res["Stephen"], res["Fongka"],
            f"{winner} {mode} {fan}番"
        ]
        
        with st.spinner('同步中... 唔好閂埋個 App'):
            save_to_gsheet(new_row)
        
        st.success("✅ 數據已寫入 Google Sheet！")
        st.rerun()
