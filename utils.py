import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from datetime import datetime

def get_connection():
    creds_dict = st.secrets["connections"]["gsheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

def get_base_money(fan):
    fan_map = {3: 8, 4: 16, 5: 48, 6: 64, 7: 96, 8: 128, 9: 192, 10: 256}
    return fan_map.get(fan, 256 if fan > 10 else 0)

@st.cache_data(ttl=5)
def load_master_data(spreadsheet_url, worksheet_name, players):
    # 使用 Streamlit 原生連線讀取數據
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=spreadsheet_url, worksheet=worksheet_name).dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'])
    for p in players:
        df[p] = pd.to_numeric(df[p], errors='coerce').fillna(0)
    return df
