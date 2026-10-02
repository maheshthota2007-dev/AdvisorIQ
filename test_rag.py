from rag import get_retriever


retriever = get_retriever(k=2)

question = "What risks should investors consider when researching Apple?"

results = retriever.invoke(question)

print("\n===== RAG RESULTS =====\n")

for i, document in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(document.page_content)
    print("Source:", document.metadata.get("source"))
    print()