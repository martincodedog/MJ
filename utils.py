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
def load_master_data(url, sheet_name, players):
    # 直接使用傳入的 url，不要再手動拼接 &gid=...
    # 因為我們在 app.py 已經定義好正確的純數字 GID URL 了
    try:
        df = pd.read_csv(url)
        
        # 確保 Date 欄位轉換為日期格式
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
