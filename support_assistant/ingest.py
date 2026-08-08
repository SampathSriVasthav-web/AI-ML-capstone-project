import os
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Paths
# --------------------------------------------------

DOCS_DIR = "support_assistant/docs"
CHROMA_DIR = "support_assistant/chroma_db"


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# Create ChromaDB client
# --------------------------------------------------

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)


# --------------------------------------------------
# Create collection
# --------------------------------------------------

collection = client.get_or_create_collection(
    name="zepto_policies"
)


# --------------------------------------------------
# Load documents
# --------------------------------------------------

documents = []
ids = []
metadatas = []


for filename in sorted(os.listdir(DOCS_DIR)):

    if filename.endswith(".txt"):

        filepath = os.path.join(DOCS_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read().strip()

        documents.append(text)
        ids.append(filename.replace(".txt", ""))

        metadatas.append({
            "source": filename
        })


# --------------------------------------------------
# Create embeddings
# --------------------------------------------------

embeddings = model.encode(
    documents
).tolist()


# --------------------------------------------------
# Store in ChromaDB
# --------------------------------------------------

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


print("Documents loaded:", len(documents))
print("Collection:", collection.name)
print("Total records:", collection.count())