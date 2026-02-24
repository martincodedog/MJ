import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard(df_master, players):
    st.header("📊 專業數據分析系統")
    
    # Metrics
    m_cols = st.columns(len(players))
    for i, p in enumerate(players):
        total = df_master[p].sum()
        recent = df_master[p].tail(5).values
        pred_val = np.average(recent, weights=np.arange(1, len(recent)+1)) if len(recent) >= 3 else 0
        m_cols[i].metric(label=f"{p} 累積結餘", value=f"${total:,.0f}", delta=f"趨勢: {pred_val:+.1f}")

    st.divider()
    st.subheader("📈 歷史戰鬥力走勢")
    st.line_chart(df_master.set_index("Date")[players].cumsum())

    st.divider()
    st.subheader("📋 核心表現摘要 (KPIs)")
    stats_df = []
    for p in players:
        p_data = df_master[p]
        total_days = len(p_data)
        stats_df.append({
            "玩家": p,
            "對局總天數": total_days,
            "勝率 (%)": f"{((p_data > 0).sum()/total_days*100):.1f}%" if total_days > 0 else "0%",
            "場均盈虧": f"${p_data.mean():.1f}",
            "風險值": f"{p_data.std():.1f}"
        })
    st.table(pd.DataFrame(stats_df).set_index("玩家"))
