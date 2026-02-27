from fastapi import FastAPI, Depends, Form, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import json
import os
import re
import sqlite3
import google.generativeai as genai
import models
import schemas
from database import engine, get_db, load_csv_to_sqlite
from auth import hash_password, verify_password, create_access_token, get_current_user

models.Base.metadata.create_all(bind=engine)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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


@app.post("/upload")
def upload_csv(file: UploadFile = File(...)):
    """
    Upload CSV file and load data into SQLite database.
    
    Accepts CSV file, cleans column names, and loads into data_table.
    """
    temp_file_path = "temp.csv"
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
        
        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Load CSV into SQLite
        result = load_csv_to_sqlite(temp_file_path)
        
        return {
            "message": "File uploaded and data loaded successfully",
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



def get_table_schema() -> str:
    """
    Extract schema of data_table using PRAGMA table_info.
    
    Returns:
        Formatted schema string
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(data_table)")
    schema_info = cursor.fetchall()
    conn.close()
    
    schema = "Table: data_table\nColumns:\n"
    for col in schema_info:
        schema += f"- {col[1]} ({col[2]})\n"
    
    return schema


def generate_sql(question: str, schema: str) -> str:
    """
    Generate SQL query using Gemini API.
    
    Args:
        question: Natural language question
        schema: Database schema
        
    Returns:
        Generated SQL query
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""You are a SQL expert. Generate a SQL query based on the user question and database schema.

Database Schema:
{schema}

User Question: {question}

CRITICAL RULES:
- Use ONLY the table name: data_table
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
    Execute SQL query and return results.
    
    Args:
        sql_query: SQL query to execute
        
    Returns:
        dict with columns and rows
        
    Raises:
        Exception: If query execution fails
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        return {
            "columns": columns,
            "rows": rows
        }
    finally:
        conn.close()


def generate_answer(question: str, columns: list, rows: list) -> str:
    """
    Generate natural language answer from query results.
    
    Args:
        question: Original user question
        columns: Column names from query result
        rows: Data rows from query result
        
    Returns:
        Natural language explanation
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""You are a data analyst. Generate a short, clear answer to the user's question based strictly on the query results.

User Question: {question}

Query Results:
Columns: {columns}
Data: {rows}

CRITICAL RULES:
- Base your answer ONLY on the provided data
- Do not make assumptions or add external information
- Do not hallucinate
- Keep the answer concise and factual
- If the result is empty, say "No data found"

Answer:"""
    
    response = model.generate_content(prompt)
    return response.text.strip()


@app.post("/query", response_model=schemas.QueryResponse)
def query_data(question_input: schemas.QuestionInput):
    """
    Process natural language question and return SQL results with explanation.
    """
    try:
        # Extract schema
        schema = get_table_schema()
        
        # Generate SQL using LLM
        sql_query = generate_sql(question_input.question, schema)
        
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
            result["columns"],
            result["rows"]
        )
        
        return {
            "answer": answer,
            "sql_query": sql_query,
            "columns": result["columns"],
            "rows": result["rows"]
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
