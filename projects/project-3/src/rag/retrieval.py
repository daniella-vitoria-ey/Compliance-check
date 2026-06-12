import os
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("docs")

def retrieve(query: str, top_k: int = 3):
    data = collection.get(include=["documents", "metadatas"])

    docs = data["documents"]
    metas = data["metadatas"]

    logger.info(f"Total de docs no banco: {len(docs)}")

    if not docs:
        return []

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(docs + [query]).toarray()

    query_vec = vectors[-1].reshape(1, -1)
    doc_vecs = vectors[:-1]

    scores = cosine_similarity(doc_vecs, query_vec).flatten()
    top_idx = scores.argsort()[-top_k:][::-1]

    logger.info(f"Top indices: {top_idx}")

    results = [
        {
            "text": docs[i],
            "source": metas[i]["source"],
            "chunk_id": metas[i]["chunk_id"]
        }
        for i in top_idx
    ]

    return results