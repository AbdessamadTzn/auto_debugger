"""
Système de patch pour modifier les fichiers source
"""
import shutil
from pathlib import Path
from datetime import datetime
import config


class CodePatcher:
    """Applique les corrections sur les fichiers source"""
    
    def __init__(self, backup_dir: str = None):
        """
        Args:
            backup_dir: Dossier pour les backups
        """
        self.backup_dir = Path(backup_dir) if backup_dir else config.BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """
        Crée une sauvegarde du fichier
        
        Args:
            file_path: Chemin du fichier à sauvegarder
        
        Returns:
            Chemin du backup
        """
        file_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        print(f"💾 Backup créé : {backup_path}")
        return str(backup_path)
    
    def apply_fixes(self, fixes: list, base_path: str) -> bool:
        """
        Applique toutes les corrections
        
        Args:
            fixes: Liste des corrections (du JSON Groq)
            base_path: Chemin de base du projet
        
        Returns:
            True si succès, False sinon
        """
        base_path = Path(base_path)
        
        # Grouper les fixes par fichier
        files_to_fix = {}
        for fix in fixes:
            file_name = fix['file']
            if file_name not in files_to_fix:
                files_to_fix[file_name] = []
            files_to_fix[file_name].append(fix)
        
        # Appliquer les corrections fichier par fichier
        for file_name, file_fixes in files_to_fix.items():
            # Déterminer le chemin complet
            if Path(file_name).is_absolute():
                file_path = Path(file_name)
            else:
                file_path = base_path / file_name
            
            if not file_path.exists():
                print(f"⚠️  Fichier introuvable : {file_path}")
                continue
            
            # Créer un backup
            self.create_backup(file_path)
            
            # Appliquer les corrections
            success = self._patch_file(file_path, file_fixes)
            if not success:
                print(f"❌ Échec du patch pour {file_name}")
                return False
        
        return True
    
    def _patch_file(self, file_path: Path, fixes: list) -> bool:
        """
        Applique les corrections sur un fichier
        
        Args:
            file_path: Chemin du fichier
            fixes: Liste des corrections pour ce fichier
        
        Returns:
            True si succès
        """
        # Lire le fichier
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Erreur lecture : {e}")
            return False
        
        # Trier les fixes par numéro de ligne (décroissant pour éviter les décalages)
        fixes_sorted = sorted(fixes, key=lambda x: x['line_to_remove'], reverse=True)
        
        # Appliquer chaque fix
        for fix in fixes_sorted:
            line_to_remove = fix['line_to_remove']
            line_to_add = fix['line_to_add']
            position = fix['position']
            reason = fix['reason']
            
            print(f"\n🔧 Application du fix :")
            print(f"   Ligne {line_to_remove} : Suppression")
            print(f"   Ligne {position} : Insertion")
            print(f"   Raison : {reason}")
            
            # Vérifier la validité
            if line_to_remove < 1 or line_to_remove > len(lines):
                print(f"⚠️  Ligne {line_to_remove} invalide (fichier a {len(lines)} lignes)")
                continue
            
            # Supprimer la ligne (index = numéro - 1)
            removed_line = lines.pop(line_to_remove - 1)
            print(f"   ❌ Supprimé : {removed_line.strip()}")
            
            # Insérer la nouvelle ligne
            # Ajuster la position si nécessaire
            insert_index = min(position - 1, len(lines))
            if not line_to_add.endswith('\n'):
                line_to_add += '\n'
            lines.insert(insert_index, line_to_add)
            print(f"   ✅ Ajouté : {line_to_add.strip()}")
        
        # Écrire le fichier modifié
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n✅ Fichier modifié : {file_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur écriture : {e}")
            return False
    
    def restore_backup(self, backup_path: str, original_path: str) -> bool:
        """
        Restaure un backup
        
        Args:
            backup_path: Chemin du backup
            original_path: Chemin du fichier original
        
        Returns:
            True si succès
        """
        try:
            shutil.copy2(backup_path, original_path)
            print(f"♻️  Backup restauré : {original_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur restauration : {e}")
            return False