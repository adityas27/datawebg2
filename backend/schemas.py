from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email_id: EmailStr
    first_name: str
    last_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email_id: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int


# --- Text-to-SQL schemas ---

class QuestionInput(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sql_query: str
    result: list | None = None
    error: str | None = None