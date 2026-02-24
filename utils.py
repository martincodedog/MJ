# utils.py
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 喺呢度貼上你份 Sheet 嘅網址 (記得要先喺 Sheet 度 Share 畀 "Anyone with the link can edit")
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit?gid=2131114078#gid=2131114078"

def load_master_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 直接傳入 URL
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    return df

def save_to_gsheet(new_row_list):
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 讀取現有數據
    existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
    
    # 建立新 row
    new_df = pd.DataFrame([new_row_list], columns=existing_df.columns)
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # 寫入 (update 會覆蓋成個 worksheet，所以要傳入完整 updated_df)
    conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_df)
