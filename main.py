# codecraft/main.py
import os
# --- CHANGEMENT ICI ---
from codecraft.core.llm_backend import GeminiWrapper 
from codecraft.memory.vector_store import ChromaVectorStore
from codecraft.verification.static_analyzer import PythonStaticAnalyzer
from codecraft.agent.react_engine import CodeCraftAgent

def main():
    print("🚀 Initialisation de CodeCraft (Moteur: Gemini 2.5 Flash)...")
    
    # Récupération de la clé (Variable d'env ou input direct)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Collez votre clé API Google AI Studio : ")

    # 1. Initialisation du LLM
    try:
        llm = GeminiWrapper(api_key=api_key, model_name="gemini-2.5-flash")
    except Exception as e:
        print(f"❌ Erreur d'initialisation Gemini: {e}")
        return

    # 2. Le reste ne change pas (C'est la beauté du modulaire)
    memory = ChromaVectorStore()
    
    # Assurez-vous d'avoir gardé le static_analyzer robuste qu'on a fait avant
    verifier = PythonStaticAnalyzer() 
    
    agent = CodeCraftAgent(llm, memory, verifier)
    
    # 3. Simulation : On "lit" un fichier existant dans la mémoire
    # Imaginons que ceci est le contenu d'un fichier 'pricing.py' sur le disque
    file_content = """
import os

def calculate_price(base):
    # Legacy pricing logic
    tax = base * 0.2
    total = base + tax
    eval(f"print('Logging price: {total}')") # Security flaw
    return total

class UserAuth:
    def login(self, creds):
        pass
"""
    # L'agent découpe ce fichier via AST et stocke les fonctions séparément
    memory.add_code_artifact(file_content, {"filename": "pricing.py"})
    
    # 4. Exécution
    # Grâce au RAG, l'agent va retrouver SEULEMENT la fonction calculate_price
    # même si on ne lui donne pas explicitement.
    task = "Il y a une faille de sécurité dans le calcul des prix. Corrige-la."
    
    print("\n--- Démarrage de l'Agent ---")
    result = agent.run(task)
    
    print("\n--- RÉSULTAT FINAL ---")
    print(result)

if __name__ == "__main__":
    main()
