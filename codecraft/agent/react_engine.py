import re
from codecraft.core.interfaces import LLMInterface, MemoryInterface, VerifierInterface

class CodeCraftAgent:
    def __init__(self, 
                 llm: LLMInterface, 
                 memory: MemoryInterface, 
                 verifier: VerifierInterface):
        self.llm = llm
        self.memory = memory
        self.verifier = verifier

    def _extract_code_block(self, text: str) -> str:
        """
        Extraction robuste:
        1. Cherche les balises markdown ```python ... ```
        2. Cherche les balises markdown génériques ``` ... ```
        3. FALLBACK: Cherche le premier mot-clé Python (def, class, import)
        """
        # Nettoyage préliminaire
        text = text.strip()
        
        # 1. & 2. Markdown Extraction
        # On cherche ``` puis optionnellement python, puis le contenu, puis ```
        pattern = r"```(?:python)?\s*(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # On prend le bloc le plus long (souvent le code principal)
            return max(matches, key=len).strip()
            
        # 3. Fallback heuristique (Si le modèle oublie les balises markdown)
        # On cherche où le code commence vraiment
        lines = text.split('\n')
        code_lines = []
        started = False
        
        for line in lines:
            stripped = line.strip()
            # Si on n'a pas commencé, on cherche un déclencheur
            if not started:
                if stripped.startswith(('def ', 'class ', 'import ', 'from ', '@')):
                    started = True
                    code_lines.append(line)
            else:
                # Une fois commencé, on garde tout (sauf les textes de fin de conversation)
                if stripped.lower().startswith(("note:", "hope this helps", "explanation:")):
                    break
                code_lines.append(line)
        
        if code_lines:
            return "\n".join(code_lines).strip()
            
        # Si tout échoue, on renvoie le texte brut (et ça plantera probablement, mais on le verra)
        return text

    def run(self, user_instruction: str, max_retries=3):
        # 1. Retrieval
        context = self.memory.retrieve_relevant(user_instruction)
        
        # 2. Prompt Formaté pour Qwen/Mistral (ChatML format)
        # Cela aide le modèle à distinguer les instructions du contenu
        prompt_content = f"""
CONTEXTE DU CODE:
{context}

TACHE:
{user_instruction}

RÈGLES STRICTES:
1. Renvoie UNIQUEMENT du code Python valide.
2. PAS d'explications, PAS de texte avant ou après.
3. Utilise des balises Markdown ```python ... ```.
4. Le code doit être complet (imports inclus).
"""
        
        # Utilisation des balises spéciales si supportées par le prompt, sinon texte brut clair
        final_prompt = f"<|im_start|>system\nTu es un expert Python silencieux. Tu ne parles qu'en code.\n<|im_end|>\n<|im_start|>user\n{prompt_content}\n<|im_end|>\n<|im_start|>assistant\n"

        current_code = ""
        error_log = ""

        for attempt in range(max_retries):
            print(f"\n--- Cycle {attempt + 1}/{max_retries} ---")
            
            if error_log:
                final_prompt += f"Le code précédent comportait des erreurs :\n{error_log}\nCorrige le code.\n"

            # Génération
            raw_response = self.llm.generate(final_prompt)
            
            # Extraction
            current_code = self._extract_code_block(raw_response)
            
            # --- DEBUG VITAL : AFFICHER CE QU'ON ESSAIE DE COMPILER ---
            print(f"🔎 DEBUG: Code extrait (début):\n---")
            print('\n'.join(current_code.split('\n')[:5])) # Affiche les 5 premières lignes
            print("...\n---")
            # ----------------------------------------------------------

            if not current_code:
                print("⚠️  Extraction vide. Le LLM n'a rien renvoyé d'utile.")
                continue

            # Vérification
            result = self.verifier.verify(current_code)
            
            if result['valid']:
                print("✅ Code validé.")
                return current_code
            else:
                print(f"❌ Erreur Analyseur: {result['errors']}")
                error_log = result['errors']

        return f"# ECHEC\n{current_code}"
