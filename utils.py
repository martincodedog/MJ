import pandas as pd
import os

# 設定 CSV 檔案名稱
CSV_FILE = "mahjong_data.csv"

def load_master_data(players):
    """從 CSV 載入數據，若檔案不存在則建立一個初始範本"""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date"] + players + ["Remark"])
        df.to_csv(CSV_FILE, index=False)
        return df
    
    # 讀取並確保日期格式正確
    df = pd.read_csv(CSV_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def save_to_csv(new_row_list):
    """將新對局數據附加到 CSV 檔案中"""
    # 載入現有數據
    df = pd.read_csv(CSV_FILE)
    # 建立新列（確保欄位順序與 CSV 一致）
    new_df = pd.DataFrame([new_row_list], columns=df.columns)
    # 合併並儲存
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def get_base_money(fan):
    """
    麻將番數對應表 (底分計算)
    3番:$8, 4番:$16, 5番:$32, 6番:$48, 7番:$64, 8番:$96, 9番:$128, 10番:$192
    """
    mapping = {
        3: 8, 
        4: 16, 
        5: 32, 
        6: 48, 
        7: 64, 
        8: 96, 
        9: 128, 
        10: 192
    }
    return mapping.get(fan, 0)
