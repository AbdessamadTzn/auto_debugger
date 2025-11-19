"""
Module de patch pour l'Agent de Debugging Python Automatique.
Applique les corrections au fichier source selon le format JSON strict.
"""

import os
from typing import Dict, List, Any, Optional


def apply_corrections(file_path: str, corrections_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applique les corrections au fichier source.
    
    Args:
        file_path: Chemin vers le fichier à corriger
        corrections_data: Dictionnaire JSON contenant les corrections au format:
            {
                "file": "file_to_correct.py",
                "corrections": [
                    {
                        "action": "replace" | "insert" | "delete",
                        "line_number": 12,
                        "new_content": "nouvelle ligne de code"  # Requis pour replace/insert
                    }
                ]
            }
    
    Returns:
        Dictionnaire avec le résultat:
        - 'success': bool - True si les corrections ont été appliquées
        - 'message': str - Message de statut
        - 'backup_path': str - Chemin vers le fichier de sauvegarde (si créé)
    """
    if not os.path.exists(file_path):
        return {
            'success': False,
            'message': f"Le fichier n'existe pas: {file_path}",
            'backup_path': None
        }
    
    # Vérifie que le fichier dans les corrections correspond
    if corrections_data.get("file") != os.path.basename(file_path):
        # Utilise quand même le fichier fourni
        pass
    
    corrections = corrections_data.get("corrections", [])
    if not corrections:
        return {
            'success': False,
            'message': "Aucune correction à appliquer",
            'backup_path': None
        }
    
    # Trie les corrections par numéro de ligne (décroissant pour éviter les décalages)
    sorted_corrections = sorted(corrections, key=lambda x: x.get("line_number", 0), reverse=True)
    
    try:
        # Lit le fichier source
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Crée une sauvegarde
        backup_path = _create_backup(file_path)
        
        # Applique les corrections
        modified_lines = lines.copy()
        
        for correction in sorted_corrections:
            action = correction.get("action")
            line_number = correction.get("line_number")
            new_content = correction.get("new_content", "")
            
            if line_number < 1 or line_number > len(modified_lines):
                continue
            
            # Index 0-based
            index = line_number - 1
            
            if action == "replace":
                # Remplace la ligne
                modified_lines[index] = new_content.rstrip() + '\n'
            
            elif action == "insert":
                # Insère une nouvelle ligne après la ligne spécifiée
                # Si line_number = 5, insère après la ligne 5 (index 4)
                insert_line = new_content.rstrip() + '\n'
                modified_lines.insert(index, insert_line)
            
            elif action == "delete":
                # Supprime la ligne
                modified_lines.pop(index)
        
        # Écrit le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        return {
            'success': True,
            'message': f"{len(corrections)} correction(s) appliquée(s) avec succès",
            'backup_path': backup_path
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Erreur lors de l'application des corrections: {str(e)}",
            'backup_path': None
        }


def _create_backup(file_path: str) -> str:
    """
    Crée une sauvegarde du fichier avant modification.
    
    Args:
        file_path: Chemin vers le fichier à sauvegarder
    
    Returns:
        Chemin vers le fichier de sauvegarde
    """
    import shutil
    from datetime import datetime
    
    # Génère un nom de fichier de sauvegarde avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    backup_name = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(os.path.dirname(file_path), backup_name)
    
    # Copie le fichier
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def preview_corrections(file_path: str, corrections_data: Dict[str, Any]) -> List[str]:
    """
    Affiche un aperçu des corrections sans les appliquer.
    
    Args:
        file_path: Chemin vers le fichier
        corrections_data: Dictionnaire JSON contenant les corrections
    
    Returns:
        Liste de chaînes décrivant les corrections
    """
    if not os.path.exists(file_path):
        return [f"Erreur: Le fichier n'existe pas: {file_path}"]
    
    corrections = corrections_data.get("corrections", [])
    preview = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for correction in corrections:
            action = correction.get("action")
            line_number = correction.get("line_number")
            new_content = correction.get("new_content", "")
            
            if line_number < 1 or line_number > len(lines):
                preview.append(f"Ligne {line_number}: Erreur - ligne hors limites")
                continue
            
            old_line = lines[line_number - 1].rstrip()
            
            if action == "replace":
                preview.append(
                    f"Ligne {line_number} - REMPLACER:\n"
                    f"  Ancien: {old_line}\n"
                    f"  Nouveau: {new_content}"
                )
            elif action == "insert":
                preview.append(
                    f"Ligne {line_number} - INSÉRER APRÈS:\n"
                    f"  Contenu: {new_content}"
                )
            elif action == "delete":
                preview.append(
                    f"Ligne {line_number} - SUPPRIMER:\n"
                    f"  Contenu: {old_line}"
                )
    
    except Exception as e:
        preview.append(f"Erreur lors de la prévisualisation: {str(e)}")
    
    return preview

