from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import pandas as pd

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_csv_to_sqlite(file_path: str) -> dict:
    """
    Load CSV file into SQLite database.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        dict with columns and rows_loaded
        
    Raises:
        Exception: If file reading or database operation fails
    """
    conn = None
    try:
        # Read CSV using pandas
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Connect to SQLite database
        conn = sqlite3.connect("app.db")
        
        # Load data into SQLite, replacing existing table
        df.to_sql("data_table", conn, if_exists="replace", index=False)
        
        # Get metadata
        columns = df.columns.tolist()
        rows_loaded = len(df)
        
        return {
            "columns": columns,
            "rows_loaded": rows_loaded
        }
        
    finally:
        if conn:
            conn.close()