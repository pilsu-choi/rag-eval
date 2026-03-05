async def full_text_search(question):
    retrieved_docs = ["doc1", "doc2", "doc3"]
    return {
        "question": question,
        "retrieved_docs": retrieved_docs,
    }