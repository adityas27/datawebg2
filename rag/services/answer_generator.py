from config import model

def generate_answer(question: str, result):

    prompt = f"""
You are a data analyst.

Using ONLY the result below, answer the user's question.

Do NOT add any new numbers.
Do NOT make assumptions.

Question:
{question}

Query Result:
{result}

Provide a clear business explanation.
"""

    response = model.generate_content(prompt)

    return response.text.strip()