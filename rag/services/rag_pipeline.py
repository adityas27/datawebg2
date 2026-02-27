from services.data_loader import load_data
from services.schema_extractor import extract_schema
from services.query_generator import generate_query
from services.query_executor import execute_query
from services.answer_generator import generate_answer

def answer_question(question: str):

    df = load_data()

    schema = extract_schema(df)

    query_code = generate_query(question, schema)

    result = execute_query(df, query_code)

    explanation = generate_answer(question, result)

    return {
        "answer": explanation,
        "query_used": query_code,
        "raw_result": str(result),
        "explanation": "Answer derived strictly from executed pandas query on dataset."
    }