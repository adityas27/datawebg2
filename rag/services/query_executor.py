def execute_query(df, code: str):
    local_vars = {"df": df}

    try:
        result = eval(code, {}, local_vars)
        return result
    except Exception as e:
        return {"error": str(e)}