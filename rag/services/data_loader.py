import pandas as pd

DATA_PATH = r"D:\Dataweb\datawebg2\rag\dataset\Telco Customer Churn.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)

    # Fix TotalCharges column
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    df = df.dropna()

    return df