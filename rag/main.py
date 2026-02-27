from services.rag_pipeline import answer_question

while True:
    q = input("Ask a question: ")
    response = answer_question(q)

    print("\nAnswer:\n", response["answer"])
    print("\nQuery Used:\n", response["query_used"])
    print("\nRaw Result:\n", response["raw_result"])
    print("\n---\n")
