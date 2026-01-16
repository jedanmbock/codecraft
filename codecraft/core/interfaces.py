# codecraft/core/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class LLMInterface(ABC):
    """Interface standard pour tout modèle (OpenAI, HuggingFace, Custom Model)"""
    @abstractmethod
    def generate(self, prompt: str, stop: List[str] = None) -> str:
        pass

class MemoryInterface(ABC):
    """Interface pour la mémoire vectorielle (RAG)"""
    @abstractmethod
    def add_code_artifact(self, code: str, metadata: Dict):
        pass
        
    @abstractmethod
    def retrieve_relevant(self, query: str, k: int = 3) -> str:
        pass

class VerifierInterface(ABC):
    """Interface pour les outils d'analyse statique"""
    @abstractmethod
    def verify(self, code: str) -> Dict[str, Any]:
        """Retourne {'valid': bool, 'errors': str, 'score': float}"""
        pass
