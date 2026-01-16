# codecraft/core/llm_backend.py
import google.generativeai as genai
from typing import List
import os
from .interfaces import LLMInterface

class GeminiWrapper(LLMInterface):
    """
    Wrapper pour Google Gemini (Free Tier).
    Modèle recommandé: gemini-1.5-flash
    """
    def __init__(self, api_key: str, model_name="gemini-1.5-flash"):
        if not api_key:
            raise ValueError("API Key Gemini manquante.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def generate(self, prompt: str, stop: List[str] = None) -> str:
        try:
            # Configuration pour du code : température basse
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                stop_sequences=stop if stop else None,
                max_output_tokens=2000, # Large buffer pour le code
            )

            # Appel API
            # On désactive les filtres de sécurité excessifs qui bloquent parfois le code
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            
            return response.text

        except Exception as e:
            return f"# ERROR GEMINI: {str(e)}"
