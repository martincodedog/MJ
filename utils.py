import pandas as pd
import os
from datetime import datetime

# 設定資料夾名稱
RECORDS_DIR = "records"
MASTER_FILE = "mahjong_data.csv"

def load_master_data(players):
    """
    從兩處讀取數據：
    1. 原始的 mahjong_data.csv (歷史總表)
    2. records/ 資料夾下所有的每日 CSV
    """
    all_data = []

    # 1. 讀取原始總表 (如果存在)
    if os.path.exists(MASTER_FILE):
        df_master = pd.read_csv(MASTER_FILE)
        all_data.append(df_master)

    # 2. 讀取 records/ 資料夾內的所有每日 CSV
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR) # 自動建立資料夾
    
    for filename in os.listdir(RECORDS_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(RECORDS_DIR, filename)
            df_day = pd.read_csv(file_path)
            all_data.append(df_day)

    # 如果完全沒數據，回傳空白範本
    if not all_data:
        return pd.DataFrame(columns=["Date"] + players + ["Remark"])

    # 合併所有數據
    df_final = pd.concat(all_data, ignore_index=True)
    df_final['Date'] = pd.to_datetime(df_final['Date'])
    return df_final.sort_values(by="Date")

def save_to_csv(new_row_list, players):
    """
    將新對局存入當日的專屬 CSV (例如 records/2026-02-24.csv)
    """
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)

    # 取得今日日期作為檔名
    today_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(RECORDS_DIR, f"{today_str}.csv")
    
    # 定義欄位名稱
    columns = ["Date"] + players + ["Remark"]
    
    # 建立新列 DataFrame
    new_df = pd.DataFrame([new_row_list], columns=columns)

    if os.path.exists(file_path):
        # 如果今日檔案已存在，附加在後面
        df_today = pd.read_csv(file_path)
        df_today = pd.concat([df_today, new_df], ignore_index=True)
        df_today.to_csv(file_path, index=False)
    else:
        # 如果今日第一場，建立新檔
        new_df.to_csv(file_path, index=False)

def get_base_money(fan):
    """番數對應表"""
    mapping = {3: 8, 4: 16, 5: 32, 6: 48, 7: 64, 8: 96, 9: 128, 10: 192}
    return mapping.get(fan, 0)
