from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def rerank(query: str, documents: list, top_k: int = 3):
    if not documents:
        return []

    texts = [doc["text"] for doc in documents]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts + [query]).toarray()

    query_vec = vectors[-1].reshape(1, -1)
    doc_vecs = vectors[:-1]

    scores = cosine_similarity(doc_vecs, query_vec).flatten()

    ranked_idx = scores.argsort()[::-1]

    return [documents[i] for i in ranked_idx[:top_k]]