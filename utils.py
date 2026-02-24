import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. 喺度定義返個 URL (或者喺 st.secrets 攞)
# 確保呢條 URL 同你喺 app.py 用嘅一致
SHEET_URL = "https://docs.google.com/spreadsheets/d/12rjgnWh2gMQ05TsFR6aCCn7QXB6rpa-Ylb0ma4Cs3E4/edit?gid=2131114078#gid=2131114078"

def get_connection():
    creds_dict = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

def get_base_money(fan):
    # 呢度跟你之前嘅 logic
    fan_map = {3: 8, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
    return fan_map.get(fan, 256 if fan > 10 else 0)

@st.cache_data(ttl=5)
def load_master_data(spreadsheet_url, worksheet_name, players):
    # 使用 Streamlit 原生連線讀取數據
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=spreadsheet_url, worksheet=worksheet_name).dropna(how='all')
    
    # 轉 Date 時建議加 format='mixed' 防止報錯
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    
    for p in players:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df
