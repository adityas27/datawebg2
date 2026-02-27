import pandas as pd

def load_data(path: str):
    df = pd.read_csv(path)

    # Clean dataset
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    df = df.dropna()

    return df