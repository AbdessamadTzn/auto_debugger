"""
Module de configuration pour l'Agent de Debugging Python Automatique.
Gère les chemins du projet, l'environnement virtuel et les paramètres de configuration.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Classe pour gérer la configuration du projet."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialise la configuration.
        
        Args:
            config_file: Chemin vers un fichier de configuration JSON (optionnel)
        """
        self.project_path: Optional[str] = None
        self.venv_name: Optional[str] = None
        self.target_script: Optional[str] = None
        self.config_file = config_file or "config.json"
        
        # Charge la configuration si le fichier existe
        if os.path.exists(self.config_file):
            self.load()
    
    def set_project_path(self, path: str) -> None:
        """Définit le chemin du projet cible."""
        if os.path.exists(path):
            self.project_path = os.path.abspath(path)
        else:
            raise ValueError(f"Le chemin du projet n'existe pas: {path}")
    
    def set_venv_name(self, venv_name: str) -> None:
        """Définit le nom de l'environnement virtuel."""
        self.venv_name = venv_name
    
    def set_target_script(self, script_path: str) -> None:
        """Définit le chemin du script à déboguer."""
        if self.project_path:
            full_path = os.path.join(self.project_path, script_path)
            if os.path.exists(full_path):
                self.target_script = script_path
            else:
                raise ValueError(f"Le script n'existe pas: {full_path}")
        else:
            self.target_script = script_path
    
    def get_venv_python(self) -> Optional[str]:
        """
        Retourne le chemin vers l'exécutable Python de l'environnement virtuel.
        
        Returns:
            Chemin vers python.exe (Windows) ou python (Unix) ou None si non trouvé
        """
        if not self.project_path or not self.venv_name:
            return None
        
        venv_path = os.path.join(self.project_path, self.venv_name)
        
        # Windows
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        if os.path.exists(python_exe):
            return python_exe
        
        # Unix/Linux/Mac
        python_exe = os.path.join(venv_path, "bin", "python")
        if os.path.exists(python_exe):
            return python_exe
        
        return None
    
    def get_target_script_path(self) -> Optional[str]:
        """
        Retourne le chemin complet vers le script cible.
        
        Returns:
            Chemin complet vers le script ou None
        """
        if not self.project_path or not self.target_script:
            return None
        
        return os.path.join(self.project_path, self.target_script)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire."""
        return {
            "project_path": self.project_path,
            "venv_name": self.venv_name,
            "target_script": self.target_script
        }
    
    def save(self) -> None:
        """Sauvegarde la configuration dans un fichier JSON."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load(self) -> None:
        """Charge la configuration depuis un fichier JSON."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.project_path = data.get("project_path")
                self.venv_name = data.get("venv_name")
                self.target_script = data.get("target_script")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
    
    def is_valid(self) -> bool:
        """
        Vérifie si la configuration est valide.
        
        Returns:
            True si la configuration est complète et valide, False sinon
        """
        return (
            self.project_path is not None and
            self.venv_name is not None and
            self.target_script is not None and
            self.get_venv_python() is not None and
            self.get_target_script_path() is not None
        )

