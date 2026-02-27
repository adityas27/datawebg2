from config import model

def generate_query(question: str, schema: dict) -> str:

    schema_text = ""
    for col, details in schema.items():
        if details["type"] == "categorical":
            schema_text += f"- {col} (categorical: {details['sample_values']})\n"
        else:
            schema_text += f"- {col} (numeric)\n"

    prompt = f"""
You are generating pandas query code.

Allowed columns:
{schema_text}

Rules:
- Use ONLY these columns
- Do NOT invent columns
- Output ONLY valid pandas code using df
- Do NOT explain anything
- Result must be returned as a variable or expression

User Question:
{question}
"""

    response = model.generate_content(prompt)

    return response.text.strip()