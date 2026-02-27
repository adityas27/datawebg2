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
    user_id: int


class QuestionInput(BaseModel):
    question: str
    dataset_name: str

class QueryResponse(BaseModel):
    answer: str
    sql_query: str
    data: list[dict]

class DatasetMetadata(BaseModel):
    name: str
    table_name: str
    file_name: str
    row_count: int
    column_count: int
    file_size: int
    upload_date: str
    columns: list[str]

    class Config:
        from_attributes = True

class DatasetListItem(BaseModel):
    id: int
    name: str
    file_name: str
    row_count: int
    upload_date: str

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message: str
    dataset_name: str
    columns: list[str]
    rows_loaded: int
