#!/usr/bin/env python3
"""
Interface CLI pour Auto-Debug
Usage: auto_debug script.py [--venv path/to/venv]
"""
import argparse
import sys
import subprocess
from pathlib import Path


def launch_streamlit(script_path: str, venv_path: str = None):
    """Lance l'interface Streamlit avec les arguments"""
    
    # Construire la commande
    cmd = ["streamlit", "run", str(Path(__file__).parent / "ui_streamlit.py")]
    
    # Définir les variables d'environnement pour Streamlit
    import os
    os.environ['AUTODEBUG_SCRIPT'] = script_path
    if venv_path:
        os.environ['AUTODEBUG_VENV'] = venv_path
    
    print(f"🚀 Lancement d'Auto-Debug...")
    print(f"📄 Script : {script_path}")
    if venv_path:
        print(f"🐍 Venv : {venv_path}")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Auto-Debug fermé")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="🐞 Auto-Debug - Débogage intelligent Python avec Grok AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  auto_debug mon_script.py
  auto_debug mon_script.py --venv ./venv
  auto_debug /chemin/absolu/script.py --venv /chemin/venv
        """
    )
    
    parser.add_argument(
        'script',
        type=str,
        help='Chemin vers le script Python à déboguer'
    )
    
    parser.add_argument(
        '--venv',
        type=str,
        default=None,
        help='Chemin vers l\'environnement virtuel (optionnel)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Auto-Debug 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Vérifier que le script existe
    script_path = Path(args.script).resolve()
    if not script_path.exists():
        print(f"❌ Erreur : Le fichier '{args.script}' n'existe pas")
        sys.exit(1)
    
    if not script_path.suffix == '.py':
        print(f"⚠️  Attention : Le fichier n'a pas l'extension .py")
    
    # Vérifier le venv si spécifié
    venv_path = None
    if args.venv:
        venv_path = Path(args.venv).resolve()
        if not venv_path.exists():
            print(f"⚠️  Attention : Le venv '{args.venv}' n'existe pas")
            print(f"   Utilisation de Python système")
            venv_path = None
    
    # Lancer Streamlit
    launch_streamlit(str(script_path), str(venv_path) if venv_path else None)


if __name__ == "__main__":
    main()