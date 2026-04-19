import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from knowledge_base.docs import documents

CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorstore")

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def build_vectorstore():
    client = PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name="shopassist_faq",
        embedding_function=embedding_fn
    )
    if collection.count() == 0:
        collection.add(
            ids=[doc["id"] for doc in documents],
            documents=[doc["content"] for doc in documents],
            metadatas=[{"topic": doc["topic"]} for doc in documents]
        )
    return collection


def get_retriever():
    return build_vectorstore()


def retrieve(query: str, n_results: int = 2) -> str:
    collection = get_retriever()
    results = collection.query(query_texts=[query], n_results=n_results)
    if not results["documents"] or not results["documents"][0]:
        return ""
    docs = results["documents"][0]
    topics = [m["topic"] for m in results["metadatas"][0]]
    combined = ""
    for topic, doc in zip(topics, docs):
        combined += f"[{topic}]\n{doc}\n\n"
    return combined.strip()