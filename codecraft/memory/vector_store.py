# codecraft/memory/vector_store.py
import chromadb
from chromadb.utils import embedding_functions
import ast
import os
from typing import List, Dict
from codecraft.core.interfaces import MemoryInterface

class ChromaVectorStore(MemoryInterface):
    """
    Implémentation réelle de la mémoire épisodique (RAG).
    Utilise ChromaDB pour stocker les embeddings du code.
    """
    def __init__(self, persist_dir="./chroma_db"):
        # 1. Initialisation de la DB locale
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # 2. Fonction d'embedding (transforme le code en vecteurs mathématiques)
        # 'all-MiniLM-L6-v2' est petit, rapide et bon pour le code
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 3. Création/Récupération de la collection
        self.collection = self.client.get_or_create_collection(
            name="codebase_memory",
            embedding_function=self.ef
        )

    def _parse_code_to_chunks(self, code: str, filename: str) -> List[Dict]:
        """
        Découpage Intelligent (Hierarchical Memory - Spec 5.2).
        Utilise l'AST pour extraire les fonctions et classes proprement.
        """
        chunks = []
        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # On récupère le code source exact du noeud
                    # (Astuce: ast.get_source_segment nécessite Python 3.8+)
                    start = node.lineno - 1
                    end = node.end_lineno
                    lines = code.splitlines()
                    snippet = "\n".join(lines[start:end])
                    
                    chunks.append({
                        "id": f"{filename}::{node.name}",
                        "text": snippet,
                        "type": type(node).__name__,
                        "name": node.name
                    })
        except Exception as e:
            print(f"⚠️ Erreur parsing AST: {e}")
            # Fallback: on stocke tout le fichier si le parsing échoue
            chunks.append({"id": filename, "text": code, "type": "file", "name": filename})
            
        return chunks

    def add_code_artifact(self, code: str, metadata: Dict):
        """Ingère un fichier, le découpe et l'indexe."""
        filename = metadata.get("filename", "unknown.py")
        chunks = self._parse_code_to_chunks(code, filename)
        
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [{"type": c["type"], "filename": filename} for c in chunks]
        
        if ids:
            print(f"💾 Indexation de {len(ids)} blocs depuis {filename}...")
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

    def retrieve_relevant(self, query: str, k: int = 3) -> str:
        """Recherche sémantique : trouve le code qui 'ressemble' à la demande."""
        print(f"🔍 Recherche vectorielle pour : '{query}'")
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Formatage du contexte pour le LLM
        context = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                source = f"# Fichier: {meta['filename']} ({meta['type']})"
                context.append(f"{source}\n{doc}")
                
        return "\n\n".join(context)
