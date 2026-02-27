from fastapi import FastAPI, Depends, Form, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
import re
import sqlite3
import google.generativeai as genai
import models
import schemas
from database import engine, get_db, load_csv_to_sqlite, get_table_columns
from auth import hash_password, verify_password, create_access_token, get_current_user

models.Base.metadata.create_all(bind=engine)
print(os.getenv("GEMINI_API_KEY", ""))
# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyCagp6N4SBLW3ghbk6OxYA4Uxk0AyHY2i4"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Checking if username n email already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = db.query(models.User).filter(models.User.email_id == user.email_id).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    
    new_user = models.User(
        username=user.username,
        email_id=user.email_id,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login(
    email: str = Form(...),     
    password: str = Form(...),   
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email_id == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email_id})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "user_id": user.id}


@app.post("/upload", response_model=schemas.UploadResponse)
def upload_csv(file: UploadFile = File(...), dataset_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Upload CSV file and load data into SQLite database.
    
    Accepts CSV file, cleans column names, and loads into a unique table.
    """
    temp_file_path = "temp.csv"
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
        
        # Validate dataset name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', dataset_name):
            raise HTTPException(
                status_code=400,
                detail="Dataset name must contain only letters, numbers, and underscores"
            )
        
        # Check if dataset name already exists
        existing_dataset = db.query(models.Dataset).filter(models.Dataset.name == dataset_name).first()
        if existing_dataset:
            raise HTTPException(
                status_code=400,
                detail="Dataset name already exists. Please choose a different name."
            )
        
        # Generate unique table name
        table_name = f"dataset_{dataset_name}"
        
        # Save uploaded file temporarily
        file_content = file.file.read()
        file_size = len(file_content)
        
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Load CSV into SQLite
        result = load_csv_to_sqlite(temp_file_path, table_name)
        
        # Save dataset metadata
        new_dataset = models.Dataset(
            name=dataset_name,
            table_name=table_name,
            file_name=file.filename,
            row_count=result["rows_loaded"],
            column_count=len(result["columns"]),
            file_size=file_size,
            upload_date=datetime.now().isoformat()
        )
        
        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)
        
        return {
            "message": "File uploaded and data loaded successfully",
            "dataset_name": dataset_name,
            "columns": result["columns"],
            "rows_loaded": result["rows_loaded"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CSV file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)



def get_table_schema(table_name: str) -> str:
    """
    Extract schema of a specific table using PRAGMA table_info.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Formatted schema string
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema_info = cursor.fetchall()
    conn.close()
    
    schema = f"Table: {table_name}\nColumns:\n"
    for col in schema_info:
        schema += f"- {col[1]} ({col[2]})\n"
    
    return schema


def generate_sql(question: str, schema: str, table_name: str) -> str:
    """
    Generate SQL query using Gemini API.
    
    Args:
        question: Natural language question
        schema: Database schema
        table_name: Name of the table to query
        
    Returns:
        Generated SQL query
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""You are a SQL expert. Generate a SQL query based on the user question and database schema.

Database Schema:
{schema}

User Question: {question}

CRITICAL RULES:
- Use ONLY the table name: {table_name}
- Use ONLY columns that exist in the schema
- Return ONLY a SELECT query
- Return ONLY the SQL query, no explanation, no markdown, no comments
- Do not use backticks or code blocks
- The query must be a single line

SQL Query:"""
    
    response = model.generate_content(prompt)
    sql_query = response.text.strip()
    
    # Clean up any markdown formatting
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    return sql_query


def validate_sql(sql_query: str) -> bool:
    """
    Validate SQL query using regex.
    
    Args:
        sql_query: SQL query to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Must start with SELECT (case insensitive)
    if not re.match(r'^\s*SELECT', sql_query, re.IGNORECASE):
        return False
    
    # Must NOT contain dangerous keywords
    dangerous_keywords = [
        r'\bDROP\b', r'\bDELETE\b', r'\bINSERT\b', 
        r'\bUPDATE\b', r'\bALTER\b', r'\bPRAGMA\b',
        r'\bATTACH\b', r'\bDETACH\b'
    ]
    
    for keyword in dangerous_keywords:
        if re.search(keyword, sql_query, re.IGNORECASE):
            return False
    
    return True


def execute_sql(sql_query: str) -> dict:
    """
    Execute SQL query and return results in JSON format.
    
    Args:
        sql_query: SQL query to execute
        
    Returns:
        dict with data as list of dictionaries
        
    Raises:
        Exception: If query execution fails
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dictionaries (JSON format)
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return {
            "data": data,
            "columns": columns,
            "row_count": len(data)
        }
    finally:
        conn.close()


def generate_answer(question: str, data: list[dict], row_count: int) -> str:
    """
    Generate natural language answer from query results.

    Args:
        question: Original user question
        data: Query results as list of dictionaries
        row_count: Number of rows returned

    Returns:
        Natural language explanation
    """
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Limit data sent to LLM to avoid long outputs
    sample_data = data[:5] if len(data) > 5 else data

    prompt = f"""You are a data analyst. Generate a SHORT, concise answer to the user's question based on the query results.

User Question: {question}

Query returned {row_count} rows.
Sample data (first 5 rows): {sample_data}

CRITICAL RULES:
- Keep your answer SHORT and concise (1-3 sentences maximum)
- Do NOT list all the data rows in your answer
- Provide a summary or key insight
- If asked for specific values, mention them briefly
- If the result is empty, say "No data found"
- Do NOT include the full table in your response

Answer:"""

    response = model.generate_content(prompt)
    return response.text.strip()



@app.post("/query", response_model=schemas.QueryResponse)
def query_data(question_input: schemas.QuestionInput, db: Session = Depends(get_db)):
    """
    Process natural language question and return SQL results with explanation.
    """
    try:
        # Get dataset from database
        dataset = db.query(models.Dataset).filter(models.Dataset.name == question_input.dataset_name).first()
        
        if not dataset:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{question_input.dataset_name}' not found"
            )
        
        # Extract schema
        schema = get_table_schema(dataset.table_name)
        
        # Generate SQL using LLM
        sql_query = generate_sql(question_input.question, schema, dataset.table_name)
        
        # Validate SQL
        if not validate_sql(sql_query):
            raise HTTPException(
                status_code=400,
                detail="Generated SQL query is invalid or contains dangerous operations"
            )
        
        # Execute SQL
        result = execute_sql(sql_query)
        
        # Generate natural language answer
        answer = generate_answer(
            question_input.question,
            result["data"],
            result["row_count"]
        )
        
        return {
            "answer": answer,
            "sql_query": sql_query,
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )



@app.get("/datasets", response_model=list[schemas.DatasetListItem])
def list_datasets(db: Session = Depends(get_db)):
    """
    Get list of all uploaded datasets for the Sources panel.
    """
    datasets = db.query(models.Dataset).all()
    return datasets


@app.get("/datasets/{dataset_name}/metadata", response_model=schemas.DatasetMetadata)
def get_dataset_metadata(dataset_name: str, db: Session = Depends(get_db)):
    """
    Get detailed metadata for a specific dataset for the Table Metadata panel.
    """
    dataset = db.query(models.Dataset).filter(models.Dataset.name == dataset_name).first()
    
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{dataset_name}' not found"
        )
    
    # Get column names
    columns = get_table_columns(dataset.table_name)
    
    return {
        "name": dataset.name,
        "table_name": dataset.table_name,
        "file_name": dataset.file_name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "file_size": dataset.file_size,
        "upload_date": dataset.upload_date,
        "columns": columns
    }


@app.delete("/datasets/{dataset_name}")
def delete_dataset(dataset_name: str, db: Session = Depends(get_db)):
    """
    Delete a dataset and its associated table.
    """
    dataset = db.query(models.Dataset).filter(models.Dataset.name == dataset_name).first()
    
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{dataset_name}' not found"
        )
    
    try:
        # Drop the table from SQLite
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {dataset.table_name}")
        conn.commit()
        conn.close()
        
        # Delete metadata from database
        db.delete(dataset)
        db.commit()
        
        return {"message": f"Dataset '{dataset_name}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete dataset: {str(e)}"
        )
