#!/usr/bin/env python3
"""
Auto Debugger CLI - Débogage automatique de scripts Python avec IA
Usage: python auto_debugger.py <script.py> [--api-key KEY] [--venv PATH] [--max-iterations N]
"""

import os
import sys
import json
import subprocess
import re
import argparse
from datetime import datetime
from pathlib import Path

# Configuration par défaut
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MAX_ITERATIONS = 3
API_URL = "https://api.groq.com/openai/v1/chat/completions"


def find_python_in_venv(venv_path):
    """Trouve l'exécutable Python dans un venv."""
    venv_path = Path(venv_path)
    
    # Chemins possibles selon l'OS
    if os.name == 'nt':  # Windows
        possible_paths = [
            venv_path / 'Scripts' / 'python.exe',
            venv_path / 'bin' / 'python.exe',
        ]
    else:  # Linux/Mac
        possible_paths = [
            venv_path / 'bin' / 'python',
            venv_path / 'bin' / 'python3',
        ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    return None


def execute_script(script_path, python_exec=None, timeout=30):
    """Exécute un script Python et capture les erreurs."""
    if python_exec is None:
        python_exec = sys.executable
    
    try:
        result = subprocess.run(
            [python_exec, script_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Timeout: Le script a dépassé le temps d\'exécution',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def extract_traceback(stderr):
    """Extrait le traceback de l'erreur."""
    lines = stderr.strip().split('\n')
    traceback_start = -1
    
    for i, line in enumerate(lines):
        if line.startswith('Traceback'):
            traceback_start = i
            break
    
    if traceback_start >= 0:
        return '\n'.join(lines[traceback_start:])
    return stderr


def analyze_error_with_ai(code, error, api_key):
    """Analyse l'erreur avec l'API Groq et propose des corrections."""
    import requests
    
    prompt = f"""Tu es un expert Python. Analyse cette erreur et propose des corrections au format JSON STRICT.

CODE:
```python
{code}
```

ERREUR:
```
{error}
```

Réponds UNIQUEMENT avec un JSON valide (sans texte avant/après) :
{{
  "explanation": "explication claire de l'erreur",
  "corrections": [
    {{"action": "replace", "line": <numero>, "content": "nouveau code"}},
    {{"action": "insert", "after_line": <numero>, "content": "nouveau code"}},
    {{"action": "delete", "line": <numero>}}
  ]
}}

RÈGLES:
- Numéros de ligne en base 1 (première ligne = 1)
- Une correction par problème
- Code correct et testé"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        content = response.json()['choices'][0]['message']['content']
        
        # Extraction du JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        return json.loads(content)
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return None


def apply_corrections(script_path, corrections):
    """Applique les corrections au fichier."""
    # Sauvegarde
    backup_path = f"{script_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(script_path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original)
    
    # Lecture des lignes
    lines = original.split('\n')
    
    # Tri des corrections (delete > replace > insert pour éviter décalages)
    sorted_corrections = sorted(
        corrections,
        key=lambda x: (
            0 if x['action'] == 'delete' else 1 if x['action'] == 'replace' else 2,
            -(x.get('line', x.get('after_line', 0)))
        )
    )
    
    # Application
    for correction in sorted_corrections:
        action = correction['action']
        
        if action == 'delete':
            line_num = correction['line'] - 1
            if 0 <= line_num < len(lines):
                lines.pop(line_num)
                
        elif action == 'replace':
            line_num = correction['line'] - 1
            if 0 <= line_num < len(lines):
                lines[line_num] = correction['content']
                
        elif action == 'insert':
            after_line = correction['after_line']
            if 0 <= after_line < len(lines):
                lines.insert(after_line, correction['content'])
    
    # Sauvegarde du fichier corrigé
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return backup_path


def preview_corrections(script_path, corrections):
    """Affiche un aperçu des corrections à appliquer."""
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n" + "="*60)
    print("📋 APERÇU DES CORRECTIONS")
    print("="*60 + "\n")
    
    for i, corr in enumerate(corrections, 1):
        action = corr['action']
        print(f"🔧 Correction {i}: {action.upper()}")
        
        if action == 'delete':
            line_num = corr['line']
            print(f"   Ligne {line_num} (à supprimer):")
            if 0 < line_num <= len(lines):
                print(f"   ❌ {lines[line_num-1].rstrip()}")
        
        elif action == 'replace':
            line_num = corr['line']
            print(f"   Ligne {line_num}:")
            if 0 < line_num <= len(lines):
                print(f"   ❌ Ancien: {lines[line_num-1].rstrip()}")
                print(f"   ✅ Nouveau: {corr['content']}")
        
        elif action == 'insert':
            after_line = corr['after_line']
            print(f"   Insertion après ligne {after_line}:")
            if 0 < after_line <= len(lines):
                print(f"   📍 Après: {lines[after_line-1].rstrip()}")
            print(f"   ✅ Nouveau: {corr['content']}")
        
        print()


def ask_user_confirmation(explanation):
    """Demande confirmation à l'utilisateur avec explication."""
    print("\n" + "="*60)
    print("💡 EXPLICATION DE L'ERREUR")
    print("="*60)
    print(f"\n{explanation}\n")
    print("="*60)
    
    while True:
        response = input("\n❓ Appliquer ces corrections ? (o/n/q pour quitter): ").lower().strip()
        
        if response in ['o', 'oui', 'y', 'yes']:
            return True
        elif response in ['n', 'non', 'no']:
            return False
        elif response in ['q', 'quit', 'quitter']:
            print("\n👋 Arrêt du programme.")
            sys.exit(0)
        else:
            print("⚠️  Réponse invalide. Utilisez 'o' (oui), 'n' (non) ou 'q' (quitter).")


def main():
    parser = argparse.ArgumentParser(description='Auto Debugger CLI - Débogage automatique avec IA')
    parser.add_argument('script', help='Chemin du script Python à déboguer')
    parser.add_argument('--api-key', help='Clé API Groq (ou variable GROQ_API_KEY)')
    parser.add_argument('--venv', help='Chemin du dossier venv à utiliser')
    parser.add_argument('--max-iterations', type=int, default=DEFAULT_MAX_ITERATIONS,
                       help=f'Nombre max d\'itérations (défaut: {DEFAULT_MAX_ITERATIONS})')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout d\'exécution en secondes (défaut: 30)')
    parser.add_argument('--auto', action='store_true',
                       help='Mode automatique (pas de confirmation)')
    
    args = parser.parse_args()
    
    # Vérifications
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"❌ Fichier introuvable: {args.script}")
        sys.exit(1)
    
    api_key = args.api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Clé API Groq requise (--api-key ou variable GROQ_API_KEY)")
        sys.exit(1)
    
    # Gestion du venv
    python_exec = sys.executable
    if args.venv:
        venv_path = Path(args.venv)
        if not venv_path.exists():
            print(f"❌ Dossier venv introuvable: {args.venv}")
            sys.exit(1)
        
        python_exec = find_python_in_venv(venv_path)
        if not python_exec:
            print(f"❌ Impossible de trouver l'exécutable Python dans: {args.venv}")
            print("   Vérifiez que le dossier est bien un environnement virtuel.")
            sys.exit(1)
        
        print(f"🐍 Python trouvé: {python_exec}")
    
    print("\n🐍 Auto Debugger CLI")
    print(f"📄 Script: {script_path}")
    if args.venv:
        print(f"📦 Venv: {args.venv}")
    print(f"🔄 Max itérations: {args.max_iterations}")
    print(f"🤖 Mode: {'Automatique' if args.auto else 'Interactif'}\n")
    
    # Boucle de débogage
    for iteration in range(1, args.max_iterations + 1):
        print(f"{'='*60}")
        print(f"🔄 Itération {iteration}/{args.max_iterations}")
        print(f"{'='*60}\n")
        
        # Exécution
        print("▶️  Exécution du script...")
        result = execute_script(str(script_path), python_exec, timeout=args.timeout)
        
        if result['success']:
            print("✅ Script exécuté avec succès!")
            if result['stdout']:
                print(f"\n📤 Sortie:\n{result['stdout']}")
            break
        
        # Erreur détectée
        print("❌ Erreur détectée\n")
        error = extract_traceback(result['stderr'])
        print(f"📋 Traceback:\n{error}\n")
        
        # Analyse IA
        print("🤖 Analyse avec l'IA...")
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        analysis = analyze_error_with_ai(code, error, api_key)
        
        if not analysis or 'corrections' not in analysis:
            print("❌ Impossible d'obtenir des corrections")
            sys.exit(1)
        
        # Aperçu des corrections
        preview_corrections(str(script_path), analysis['corrections'])
        
        # Demande de confirmation (sauf en mode auto)
        if not args.auto:
            if not ask_user_confirmation(analysis['explanation']):
                print("\n⏭️  Corrections refusées. Passage à l'itération suivante...")
                continue
        else:
            print(f"\n💡 Explication: {analysis['explanation']}")
            print("\n⚡ Mode automatique: application des corrections...")
        
        # Application
        print("\n🔨 Application des corrections...")
        backup = apply_corrections(str(script_path), analysis['corrections'])
        print(f"💾 Sauvegarde créée: {backup}\n")
    
    else:
        print(f"\n⚠️  Nombre max d'itérations atteint ({args.max_iterations})")
        print("Le script contient encore des erreurs.")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("🎉 Débogage terminé avec succès!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()