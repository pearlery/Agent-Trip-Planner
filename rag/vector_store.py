from typing import List, Tuple

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = "vector_db/"
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION_NAME = "tours_collection"


class TravelVectorStore:
    def __init__(self, persist_dir: str = CHROMA_DATA_PATH):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents: List[str], metadatas: List[dict] = None, ids: List[str] = None):
        if not documents:
            return
        if ids is None:
            offset = self.collection.count()
            ids = [f"doc_{offset + i}" for i in range(len(documents))]
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
        )
        print(f"Indexed {len(documents)} documents into ChromaDB")

    def search(self, query: str, n_results: int = 3) -> Tuple[List[str], List[float], List[dict]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.count()),
        )
        docs = results["documents"][0]
        scores = [1.0 - d for d in results["distances"][0]]
        metas = results["metadatas"][0]
        return docs, scores, metas

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"},
        )


def init_vector_db(csv_path: str = "data/tours_merged_cleaned2.csv", persist_dir: str = CHROMA_DATA_PATH):
    """Initialize ChromaDB from tour CSV data. Run this once before starting the agent."""
    import pandas as pd
    from data_preprocessing import clean_text

    print("Initializing ChromaDB vector database...")

    client = chromadb.PersistentClient(path=persist_dir)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0:
        print(f"Collection already has {collection.count()} records. Skipping.")
        return

    print("Loading data...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File '{csv_path}' not found. Please check the file path.")
        return

    print("Preprocessing data...")
    df["description"] = df["description"].apply(clean_text)

    print("Preparing data...")
    ids, documents, metadatas = [], [], []
    for index, row in df.iterrows():
        ids.append(str(index))
        documents.append(str(row["description"]))
        metadatas.append({
            "program_tour": str(row.get("program_tour", "")),
            "url":          str(row.get("url", "")),
            "price":        str(row.get("price", "")),
            "region":       str(row.get("region", "")),
        })

    print("Adding data to collection...")
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Done! Total records: {collection.count()}")


if __name__ == "__main__":
    init_vector_db()
