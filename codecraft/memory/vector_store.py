# codecraft/memory/vector_store.py
from codecraft.core.interfaces import MemoryInterface

class SimpleVectorStore(MemoryInterface):
    """
    Mock d'une Vector DB. 
    Plus tard: Remplacer par ChromaDB ou FAISS avec GNN Embeddings.
    """
    def __init__(self):
        self.store = {} # Simule id -> text

    def add_code_artifact(self, code: str, metadata: dict):
        key = metadata.get('function_name', 'unknown')
        self.store[key] = code
        print(f"[Memory] Stored artifact: {key}")

    def retrieve_relevant(self, query: str, k: int = 3) -> str:
        # Simulation de recherche sémantique
        print(f"[Memory] Searching for: {query}")
        # Retourne tout le store pour la démo
        return "\n".join(self.store.values())
