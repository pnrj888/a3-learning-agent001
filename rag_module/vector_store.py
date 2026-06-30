import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import ChromaConfig
from .document_loader import DocumentLoader


class VectorStore:
    def __init__(self, collection_name: str = "computer_network"):
        self.persist_directory = ChromaConfig.PERSIST_DIRECTORY
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._init_client()

    def _init_client(self):
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "计算机网络课程知识库"}
        )

    def add_documents(self, documents: List[Dict]):
        if not documents:
            return
        
        ids = [doc["chunk_id"] for doc in documents]
        texts = [doc["content"] for doc in documents]
        metadatas = [{
            "file_name": doc["file_name"],
            "chunk_index": doc["chunk_index"],
            "total_chunks": doc["total_chunks"]
        } for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def add_pdf_files(self, pdf_dir: str = None, chunk_size: int = 500, chunk_overlap: int = 50):
        loader = DocumentLoader(pdf_dir)
        chunks = loader.process_all_pdfs(chunk_size, chunk_overlap)
        self.add_documents(chunks)
        return len(chunks)

    def query(self, query_text: str, n_results: int = 5) -> Dict:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0],
            "count": len(results["documents"][0])
        }

    def get_collection_stats(self) -> Dict:
        stats = self.collection.count()
        return {
            "total_documents": stats,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }

    def clear_collection(self):
        self.client.delete_collection(self.collection_name)
        self._init_client()

    def update_document(self, doc_id: str, new_content: str, metadata: Optional[Dict] = None):
        self.collection.update(
            ids=[doc_id],
            documents=[new_content],
            metadatas=[metadata] if metadata else None
        )

    def delete_document(self, doc_id: str):
        self.collection.delete(ids=[doc_id])
