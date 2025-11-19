"""
Configuration pour Auto-Debug
"""
import os
from pathlib import Path

# API Configuration - GROQ
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # ou "mixtral-8x7b-32768"

# Système de prompt pour Groq
SYSTEM_PROMPT = """Tu es un expert Python spécialisé dans le débogage de code.

RÈGLES STRICTES :
1. Tu réponds UNIQUEMENT en JSON valide
2. Tu analyses l'erreur Python fournie
3. Tu proposes des corrections minimales et précises
4. Si l'erreur n'est pas corrigible automatiquement, indique fixable: false

FORMAT DE RÉPONSE OBLIGATOIRE :
{
  "fixable": true/false,
  "error_type": "SyntaxError|NameError|TypeError|etc",
  "explanation": "Explication pédagogique claire en français",
  "fixes": [
    {
      "file": "nom_du_fichier.py",
      "line_to_remove": numéro_ligne,
      "line_to_add": "code corrigé",
      "position": numéro_ligne,
      "reason": "pourquoi cette correction"
    }
  ]
}

IMPORTANT :
- line_to_remove : ligne à supprimer (numéro)
- line_to_add : nouveau code à insérer
- position : où insérer la nouvelle ligne
- Si plusieurs corrections, liste-les toutes
- Sois pédagogique dans les explications
"""

# Chemins
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
BACKUP_DIR = BASE_DIR / "backups"

# Créer les dossiers nécessaires
TEMP_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)