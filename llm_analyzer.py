"""
Module d'analyse LLM pour l'Agent de Debugging Python Automatique.
Utilise l'API Groq pour analyser les erreurs et proposer des corrections.
"""

import json
import os
from typing import Dict, Any, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def analyze_error(
    source_code: str, 
    traceback: str, 
    file_path: str,
    api_key: Optional[str] = None,
    model: str = "llama3-8b-8192"
) -> Dict[str, Any]:
    """
    Analyse une erreur et retourne des corrections au format JSON strict en utilisant l'API Groq.
    
    Args:
        source_code: Code source du fichier avec l'erreur
        traceback: Traceback de l'erreur
        file_path: Chemin vers le fichier à corriger
        api_key: Clé API Groq (optionnel, utilise GROQ_API_KEY de l'environnement si non fourni)
        model: Modèle Groq à utiliser (défaut: "llama3-8b-8192")
    
    Returns:
        Dictionnaire JSON avec les corrections au format:
        {
            "file": "file_to_correct.py",
            "corrections": [
                {
                    "action": "replace" | "insert" | "delete",
                    "line_number": 12,
                    "new_content": "nouvelle ligne de code"
                }
            ]
        }
    
    Raises:
        ImportError: Si le package groq n'est pas installé
        ValueError: Si la clé API Groq n'est pas configurée
        Exception: En cas d'erreur lors de l'appel à l'API Groq
    """
    # Vérifie que Groq est disponible
    if not GROQ_AVAILABLE:
        raise ImportError(
            "Le package 'groq' est requis. Installez-le avec: pip install groq"
        )
    
    # Récupère la clé API
    groq_api_key = api_key or os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise ValueError(
            "Clé API Groq requise. "
            "Définissez la variable d'environnement GROQ_API_KEY ou passez api_key en paramètre."
        )
    
    # Initialise le client Groq
    client = Groq(api_key=groq_api_key)
    
    # Construit le prompt pour le LLM
    prompt = _build_prompt(source_code, traceback, file_path)
    
    # Appelle l'API Groq
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un expert en débogage Python. "
                    "Analyse les erreurs et propose des corrections au format JSON strict. "
                    "Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=2048,
        response_format={"type": "json_object"}
    )
    
    # Extrait la réponse JSON
    response_text = response.choices[0].message.content
    
    # Parse le JSON
    try:
        correction_data = json.loads(response_text)
        
        # Valide le format
        if validate_correction_json(correction_data):
            # Assure que le nom du fichier est correct
            correction_data["file"] = os.path.basename(file_path)
            return correction_data
        else:
            # Si le format n'est pas valide, essaie d'extraire le JSON depuis la réponse
            correction_data = _extract_json_from_response(response_text)
            if correction_data and validate_correction_json(correction_data):
                correction_data["file"] = os.path.basename(file_path)
                return correction_data
            else:
                raise ValueError("Format JSON invalide dans la réponse du LLM")
    
    except json.JSONDecodeError as e:
        # Essaie d'extraire le JSON même s'il y a du texte autour
        correction_data = _extract_json_from_response(response_text)
        if correction_data and validate_correction_json(correction_data):
            correction_data["file"] = os.path.basename(file_path)
            return correction_data
        else:
            raise ValueError(f"Impossible de parser la réponse JSON: {str(e)}")


def _build_prompt(source_code: str, traceback: str, file_path: str) -> str:
    """
    Construit le prompt pour l'API Groq.
    
    Args:
        source_code: Code source du fichier
        traceback: Traceback de l'erreur
        file_path: Chemin vers le fichier
    
    Returns:
        Prompt formaté pour le LLM
    """
    return f"""Analyse cette erreur Python et propose des corrections au format JSON strict.

Fichier: {file_path}

Code source:
```python
{source_code}
```

Erreur/Traceback:
```
{traceback}
```

Format JSON attendu:
{{
    "file": "{os.path.basename(file_path)}",
    "corrections": [
        {{
            "action": "replace",
            "line_number": 12,
            "new_content": "code corrigé"
        }}
    ]
}}

Actions possibles:
- "replace": Remplace une ligne existante (nécessite "line_number" et "new_content")
- "insert": Insère une nouvelle ligne après la ligne spécifiée (nécessite "line_number" et "new_content")
- "delete": Supprime une ligne (nécessite seulement "line_number")

Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire avant ou après."""


def _extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """
    Extrait un JSON depuis une réponse qui peut contenir du texte supplémentaire.
    
    Args:
        text: Texte contenant potentiellement du JSON
    
    Returns:
        Dictionnaire JSON extrait ou None si aucun JSON valide trouvé
    """
    # Essaie de trouver un bloc JSON dans le texte
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return None


def validate_correction_json(correction_data: Dict[str, Any]) -> bool:
    """
    Valide le format JSON de correction.
    
    Args:
        correction_data: Dictionnaire de correction à valider
    
    Returns:
        True si le format est valide, False sinon
    """
    required_keys = ["file", "corrections"]
    if not all(key in correction_data for key in required_keys):
        return False
    
    if not isinstance(correction_data["corrections"], list):
        return False
    
    valid_actions = ["replace", "insert", "delete"]
    
    for correction in correction_data["corrections"]:
        if not isinstance(correction, dict):
            return False
        
        if "action" not in correction or "line_number" not in correction:
            return False
        
        if correction["action"] not in valid_actions:
            return False
        
        if not isinstance(correction["line_number"], int):
            return False
        
        # Pour "replace" et "insert", "new_content" est requis
        if correction["action"] in ["replace", "insert"]:
            if "new_content" not in correction:
                return False
    
    return True

