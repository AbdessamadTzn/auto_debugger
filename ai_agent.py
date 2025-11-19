"""
Agent IA utilisant Groq API pour analyser et corriger les erreurs
"""
import json
import requests
from typing import Dict, Optional
from pathlib import Path
import config


class GroqAgent:
    """Agent qui communique avec Groq API pour corriger le code"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Clé API Groq (ou utilise la variable d'env)
        """
        self.api_key = api_key or config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("❌ Clé API Groq manquante ! Définissez GROQ_API_KEY")
        
        self.api_url = config.GROQ_API_URL
        self.model = config.GROQ_MODEL
    
    def analyze_error(self, script_path: str, error_info: dict) -> Optional[dict]:
        """
        Envoie le code et l'erreur à Groq pour analyse
        
        Args:
            script_path: Chemin du script bugué
            error_info: Informations sur l'erreur
        
        Returns:
            Dict avec les corrections ou None si échec
        """
        # Lire le code source
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"❌ Impossible de lire {script_path}: {e}")
            return None
        
        # Construire le prompt
        user_prompt = self._build_prompt(source_code, error_info, script_path)
        
        # Appeler Groq API
        print("🤖 Envoi à Groq pour analyse...")
        response = self._call_groq_api(user_prompt)
        
        if not response:
            return None
        
        # Parser et valider la réponse
        return self._parse_response(response)
    
    def _build_prompt(self, code: str, error_info: dict, script_path: str) -> str:
        """Construit le prompt pour Groq"""
        filename = Path(script_path).name
        
        prompt = f"""
FICHIER : {filename}

CODE SOURCE :
```python
{code}
```

ERREUR DÉTECTÉE :
Type : {error_info['error_type']}
Message : {error_info['error_message']}
Ligne : {error_info['line_number']}

TRACEBACK COMPLET :
```
{error_info['full_traceback']}
```

Analyse cette erreur et propose une correction en respectant le format JSON imposé.
"""
        return prompt
    
    def _call_groq_api(self, user_prompt: str) -> Optional[str]:
        """
        Appelle l'API Groq
        
        Args:
            user_prompt: Prompt utilisateur
        
        Returns:
            Réponse brute de Groq ou None
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extraire le contenu de la réponse
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                print("❌ Format de réponse inattendu")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API Groq : {e}")
            if hasattr(e.response, 'text'):
                print(f"   Détails : {e.response.text}")
            return None
    
    def _parse_response(self, response: str) -> Optional[dict]:
        """
        Parse et valide la réponse JSON de Groq
        
        Args:
            response: Réponse brute de Groq
        
        Returns:
            Dict validé ou None
        """
        # Nettoyer la réponse (enlever les markdown si présents)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        # Parser le JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide : {e}")
            print(f"Réponse brute : {response[:200]}...")
            return None
        
        # Valider la structure
        required_fields = ['fixable', 'error_type', 'explanation']
        for field in required_fields:
            if field not in data:
                print(f"❌ Champ manquant : {field}")
                return None
        
        # Si fixable, vérifier les fixes
        if data['fixable']:
            if 'fixes' not in data or not isinstance(data['fixes'], list):
                print("❌ Champ 'fixes' manquant ou invalide")
                return None
            
            # Valider chaque fix
            for i, fix in enumerate(data['fixes']):
                required_fix_fields = ['file', 'line_to_remove', 'line_to_add', 'position', 'reason']
                for field in required_fix_fields:
                    if field not in fix:
                        print(f"❌ Fix {i}: champ '{field}' manquant")
                        return None
        
        return data