"""
Module d'exécution pour l'Agent de Debugging Python Automatique.
Gère l'exécution du script cible et la capture des erreurs.
"""

import subprocess
import sys
import os
from typing import Dict, Optional


def execute_script(
    python_exe: str,
    script_path: str,
    working_dir: Optional[str] = None
) -> Dict[str, any]:
    """
    Exécute un script Python et capture son output et ses erreurs.
    
    Args:
        python_exe: Chemin vers l'exécutable Python (venv)
        script_path: Chemin vers le script à exécuter
        working_dir: Répertoire de travail (optionnel, défaut: répertoire du script)
    
    Returns:
        Dictionnaire contenant:
        - 'success': bool - True si l'exécution a réussi
        - 'stdout': str - Sortie standard
        - 'stderr': str - Sortie d'erreur
        - 'traceback': str - Traceback extrait (si erreur)
        - 'return_code': int - Code de retour
    """
    if not os.path.exists(python_exe):
        return {
            'success': False,
            'stdout': '',
            'stderr': f"Erreur: L'exécutable Python n'existe pas: {python_exe}",
            'traceback': '',
            'return_code': -1
        }
    
    if not os.path.exists(script_path):
        return {
            'success': False,
            'stdout': '',
            'stderr': f"Erreur: Le script n'existe pas: {script_path}",
            'traceback': '',
            'return_code': -1
        }
    
    # Détermine le répertoire de travail
    if working_dir is None:
        working_dir = os.path.dirname(os.path.abspath(script_path))
    
    try:
        # Exécute le script
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=30  # Timeout de 30 secondes
        )
        
        stdout = result.stdout
        stderr = result.stderr
        return_code = result.returncode
        
        # Extrait le traceback depuis stderr
        traceback = extract_traceback(stderr)
        
        return {
            'success': return_code == 0,
            'stdout': stdout,
            'stderr': stderr,
            'traceback': traceback,
            'return_code': return_code
        }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Erreur: Timeout lors de l\'exécution du script',
            'traceback': '',
            'return_code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f"Erreur lors de l'exécution: {str(e)}",
            'traceback': '',
            'return_code': -1
        }


def extract_traceback(stderr: str) -> str:
    """
    Extrait le traceback depuis la sortie d'erreur.
    
    Args:
        stderr: Sortie d'erreur complète
    
    Returns:
        Traceback extrait ou chaîne vide
    """
    if not stderr:
        return ''
    
    lines = stderr.split('\n')
    traceback_lines = []
    in_traceback = False
    
    for line in lines:
        # Détecte le début d'un traceback
        if 'Traceback (most recent call last)' in line:
            in_traceback = True
            traceback_lines.append(line)
        elif in_traceback:
            traceback_lines.append(line)
            # Le traceback se termine généralement par une ligne d'erreur
            # qui ne commence pas par un espace ou une tabulation
            if line.strip() and not line.startswith((' ', '\t', 'File', '  ')):
                # C'est probablement la dernière ligne du traceback
                break
    
    return '\n'.join(traceback_lines) if traceback_lines else stderr


def read_source_code(file_path: str) -> str:
    """
    Lit le contenu d'un fichier source.
    
    Args:
        file_path: Chemin vers le fichier
    
    Returns:
        Contenu du fichier en tant que chaîne
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier: {str(e)}"

