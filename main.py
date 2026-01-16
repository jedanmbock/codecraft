# codecraft/main.py
import os
# --- CHANGEMENT ICI ---
from codecraft.core.llm_backend import GeminiWrapper 
from codecraft.memory.vector_store import SimpleVectorStore
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
    memory = SimpleVectorStore()
    
    # Assurez-vous d'avoir gardé le static_analyzer robuste qu'on a fait avant
    verifier = PythonStaticAnalyzer() 
    
    agent = CodeCraftAgent(llm, memory, verifier)
    
    # 3. Données de test
    bad_code = """
def calculate_price(base):
    # Tax calculation
    tax = base * 0.2
    total = base + tax
    # Vulnerability here
    eval(f"print('Price calculated: {total}')") 
    return total
    """
    memory.add_code_artifact(bad_code, {"function_name": "calculate_price"})
    
    # 4. Exécution
    task = "La taxe est de 15%."
    
    print("\n--- Démarrage de l'Agent ---")
    result = agent.run(task)
    
    print("\n--- RÉSULTAT FINAL ---")
    print(result)

if __name__ == "__main__":
    main()
