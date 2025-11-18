"""
Exécution de scripts Python et capture d'erreurs
"""
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional


class ScriptExecutor:
    """Exécute un script Python et capture ses erreurs"""
    
    def __init__(self, venv_path: Optional[str] = None):
        """
        Args:
            venv_path: Chemin vers l'environnement virtuel
        """
        self.venv_path = Path(venv_path) if venv_path else None
        self.python_executable = self._get_python_executable()
    
    def _get_python_executable(self) -> str:
        """Récupère le chemin de l'interpréteur Python"""
        if self.venv_path:
            # Chercher l'interpréteur dans le venv
            if sys.platform == "win32":
                python_path = self.venv_path / "Scripts" / "python.exe"
            else:
                python_path = self.venv_path / "bin" / "python"
            
            if python_path.exists():
                return str(python_path)
            else:
                print(f"Venv introuvable : {python_path}")
                print(f"Utilisation de Python système")
        
        return sys.executable
    
    def execute(self, script_path: str) -> Tuple[bool, str, str, int]:
        """
        Exécute un script Python
        
        Args:
            script_path: Chemin vers le script à exécuter
        
        Returns:
            Tuple (success, stdout, stderr, returncode)
        """
        script_path = Path(script_path).resolve()
        
        if not script_path.exists():
            return False, "", f"Fichier introuvable : {script_path}", -1
        
        print(f"Exécution avec : {self.python_executable}")
        print(f"Script : {script_path}")
        
        try:
            result = subprocess.run(
                [self.python_executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,  # Timeout de 30 secondes
                cwd=script_path.parent  # Exécuter dans le dossier du script
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            return False, "", "⏱Timeout : Le script a pris trop de temps", -1
        except Exception as e:
            return False, "", f"Erreur d'exécution : {str(e)}", -1
    
    def parse_error(self, stderr: str) -> dict:
        """
        Parse l'erreur Python pour extraire les infos importantes
        
        Args:
            stderr: Sortie d'erreur du script
        
        Returns:
            Dict avec les infos de l'erreur
        """
        lines = stderr.strip().split('\n')
        
        error_info = {
            'full_traceback': stderr,
            'error_type': 'Unknown',
            'error_message': '',
            'file': '',
            'line_number': 0
        }
        
        # Extraire le type d'erreur (dernière ligne généralement)
        if lines:
            last_line = lines[-1]
            if ':' in last_line:
                error_type, error_message = last_line.split(':', 1)
                error_info['error_type'] = error_type.strip()
                error_info['error_message'] = error_message.strip()
        
        # Chercher le fichier et la ligne
        for line in lines:
            if 'File "' in line and 'line' in line:
                try:
                    # Format: File "path/to/file.py", line 42
                    parts = line.split('"')
                    if len(parts) >= 2:
                        error_info['file'] = parts[1]
                    
                    if 'line' in line:
                        line_part = line.split('line')[1].split(',')[0].strip()
                        error_info['line_number'] = int(line_part)
                except:
                    pass
        
        return error_info
