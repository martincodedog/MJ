import pandas as pd
import os

CSV_FILE = "mahjong_data.csv"

def load_master_data(players):
    """Loads data from local CSV. Creates one if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        # Create empty template
        df = pd.DataFrame(columns=["Date"] + players + ["Remark"])
        df.to_csv(CSV_FILE, index=False)
        return df
    
    df = pd.read_csv(CSV_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def save_to_csv(new_row_list):
    """Appends a single row to the CSV."""
    df = pd.read_csv(CSV_FILE)
    new_df = pd.DataFrame([new_row_list], columns=df.columns)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
