import os
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# define caminho do banco
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma")

# conecta ao banco
client = chromadb.PersistentClient(path=CHROMA_PATH)

# pega a collection criada na ingestion
collection = client.get_collection("docs")

def retrieve(query: str, top_k: int = 3):

    data = collection.get(include=["documents", "metadatas"])

    docs = data["documents"]
    metas = data["metadatas"]

    print("Total de docs no banco:", len(docs))

    if not docs:
        return []

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(docs + [query]).toarray()

    query_vec = vectors[-1].reshape(1, -1)
    doc_vecs = vectors[:-1]

    scores = cosine_similarity(doc_vecs, query_vec).flatten()

    top_idx = scores.argsort()[-top_k:][::-1]

    print("\n TOP INDICES:", top_idx)

    results = [
        {
            "text": docs[i],
            "source": metas[i]["source"],
            "chunk_id": metas[i]["chunk_id"]
        }
        for i in top_idx
    ]

    return results

# isso permite rodar direto no terminal
if __name__ == "__main__":
    results = retrieve("cliente conservador investindo em ações")

    for r in results:
        print("\n--- RESULTADO ---")
        print("Arquivo:", r["source"])
        print("Chunk:", r["chunk_id"])
        print("Texto:", r["text"])