from pathlib import Path

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


CHROMA_DIR = "chroma_store"

EMBEDDINGS = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)


def build_library(docs_dir="data/docs"):

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    docs = [
        Document(
            page_content=p.read_text(encoding="utf-8"),
            metadata={"source": str(p)}
        )
        for p in sorted(Path(docs_dir).glob("**/*"))
        if p.is_file()
    ]

    if not docs:
        raise SystemExit(
            f"No documents found in {docs_dir!r}"
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        chunks,
        EMBEDDINGS,
        persist_directory=CHROMA_DIR
    )

    print(
        f"Indexed {len(chunks)} chunks into ChromaDB"
    )


def get_retriever(k=4):

    store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=EMBEDDINGS
    )

    return store.as_retriever(
        search_kwargs={"k": k}
    )


if __name__ == "__main__":
    build_library()