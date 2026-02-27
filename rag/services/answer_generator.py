from config import model

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_answer(question: str, result):

    system_prompt = load_prompt("prompts/system_prompt_answer.txt")

    full_prompt = f"""
{system_prompt}

Question:
{question}

Query Result:
{result}
"""

    response = model.generate_content(full_prompt)

    return response.text.strip()