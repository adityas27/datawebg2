from config import model

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_query(question: str, schema: dict):

    system_prompt = load_prompt("prompts/system_prompt_query.txt")

    schema_text = ""
    for col, details in schema.items():
        if details["type"] == "categorical":
            schema_text += f"- {col} (categorical: {details['sample_values']})\n"
        else:
            schema_text += f"- {col} (numeric)\n"

    full_prompt = f"""
{system_prompt}

SCHEMA:
{schema_text}

User Question:
{question}
"""

    response = model.generate_content(full_prompt)

    return response.text.strip()