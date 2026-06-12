import os
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma")

client = chromadb.PersistentClient(path=CHROMA_PATH)

# recria coleção
try:
    client.delete_collection("docs")
except:
    pass

collection = client.create_collection("docs")


# NOVO CHUNKING (MELHORADO)
def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def run_ingestion():
    print("INICIANDO INGESTÃO")

    # caminho corrigido
    base_path = os.path.join(BASE_DIR, "knowledge_base")

    all_chunks = []
    ids = []
    metadata = []

    for file in os.listdir(base_path):
        if file.lower().endswith((".txt", ".pdf")):

            print("Processando:", file)
            full_path = os.path.join(base_path, file)

            # leitura
            if file.lower().endswith(".txt"):
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read()

            else:
                reader = PdfReader(full_path)
                pages_text = []

                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        pages_text.append(content)

                text = "\n".join(pages_text)

            # CHUNKING MELHORADO (ESSA É A MUDANÇA PRINCIPAL)
            chunks = chunk_text(text)

            for i, chunk in enumerate(chunks):
                chunk = chunk.strip()

                if not chunk:
                    continue

                all_chunks.append(chunk)
                ids.append(f"{file}_{i}")
                metadata.append({
                    "source": file,
                    "chunk_id": f"{file}_{i}"
                })

    if not all_chunks:
        print("Nenhum texto encontrado!")
        return

    # vetoriza
    vectorizer = TfidfVectorizer()
    embeddings = vectorizer.fit_transform(all_chunks).toarray()

    collection.add(
        documents=all_chunks,
        embeddings=embeddings.tolist(),
        ids=ids,
        metadatas=metadata
    )

    print("Ingestão concluída!")
    print("Total de chunks:", len(all_chunks))

if __name__ == "__main__":
    run_ingestion()