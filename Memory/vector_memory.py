import os
import chromadb
from chromadb.utils import embedding_functions

class VectorMemory:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "parmana_memory"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using default sentence-transformers embedding function if none provided
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef
        )

    def add_memory(self, text: str, metadata: dict = None, memory_id: str = None):
        """Add a document to long term memory."""
        import uuid
        doc_id = memory_id if memory_id else str(uuid.uuid4())
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{"type": "conversation_snippet"}],
            ids=[doc_id]
        )
        return doc_id

    def search_memory(self, query: str, n_results: int = 3) -> list:
        """Search the long-term memory for relevant entries."""
        if self.collection.count() == 0:
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results and "documents" in results and results["documents"]:
            return results["documents"][0] # Return the list of top matches
        return []

# Initialize global vector memory instance placeholder, will be instantiated by main/agent
vector_memory = None
def initialize_vector_memory(path):
    global vector_memory
    vector_memory = VectorMemory(db_path=path)
