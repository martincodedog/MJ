import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 填入你啱啱 Copy 嘅 URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit?gid=2131114078#gid=2131114078"

def load_master_data():
    """從 Google Sheet 抓取所有數據"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 設定 ttl=0 確保每次都係攞最新數據，唔好用快取
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    return df

def save_to_gsheet(new_row_list):
    """將新數據 append 入 Google Sheet"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    existing_df = conn.read(spreadsheet=SHEET_URL, worksheet="Master Record", ttl=0)
    
    # 建立新一行
    new_df = pd.DataFrame([new_row_list], columns=existing_df.columns)
    
    # 合併舊數同新數
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # 寫返入 Google Sheet
    conn.update(spreadsheet=SHEET_URL, worksheet="Master Record", data=updated_df)

def get_base_money(fan):
    mapping = {3: 8, 4: 16, 5: 32, 6: 48, 7: 64, 8: 96, 9: 128, 10: 192}
    return mapping.get(fan, 0)
