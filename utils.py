import pandas as pd
import os
from datetime import datetime

# 設定資料夾名稱
RECORDS_DIR = "records"
MASTER_FILE = "mahjong_data.csv"

def load_master_data(players):
    all_data = []

    # 1. 讀取原始總表
    if os.path.exists(MASTER_FILE):
        df_master = pd.read_csv(MASTER_FILE)
        all_data.append(df_master)

    # 2. 讀取 records/ 資料夾內的所有每日 CSV
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)
    
    for filename in os.listdir(RECORDS_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(RECORDS_DIR, filename)
            df_day = pd.read_csv(file_path)
            all_data.append(df_day)

    if not all_data:
        return pd.DataFrame(columns=["Date"] + players + ["Remark"])

    # 合併數據
    df_final = pd.concat(all_data, ignore_index=True)
    
    # --- 修正點：使用 format='mixed' 來兼容 2024/01/01 和 2024-01-01 ---
    df_final['Date'] = pd.to_datetime(df_final['Date'], format='mixed')
    
    return df_final.sort_values(by="Date")

def save_to_csv(new_row_list, players):
    # 1. 獲取絕對路徑，防止路徑偏離
    current_dir = os.path.dirname(os.path.abspath(__file__))
    records_dir = os.path.join(current_dir, "records")
    
    # 2. 如果資料夾不存在，強制建立
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
    
    # 3. 檔名包含日期
    today_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(records_dir, f"{today_str}.csv")
    
    columns = ["Date"] + players + ["Remark"]
    new_df = pd.DataFrame([new_row_list], columns=columns)

    try:
        if os.path.exists(file_path):
            df_today = pd.read_csv(file_path)
            df_today = pd.concat([df_today, new_df], ignore_index=True)
            df_today.to_csv(file_path, index=False)
        else:
            new_df.to_csv(file_path, index=False)
        return True # 代表成功
    except Exception as e:
        st.error(f"存檔失敗: {e}") # 在頁面上直接顯示錯誤
        return False

def get_base_money(fan):
    """番數對應表"""
    mapping = {3: 8, 4: 16, 5: 32, 6: 48, 7: 64, 8: 96, 9: 128, 10: 192}
    return mapping.get(fan, 0)
