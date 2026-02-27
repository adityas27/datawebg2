from fastapi import FastAPI, Depends, Form, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import json
import os
import models
import schemas
from database import engine, get_db, load_csv_to_sqlite
from auth import hash_password, verify_password, create_access_token, get_current_user

models.Base.metadata.create_all(bind=engine)

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