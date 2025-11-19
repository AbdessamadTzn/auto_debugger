# 🚀 Guide de démarrage rapide - Auto Debug

## Installation

### Option 1 : Installation en mode développement (recommandé)

```bash
# Depuis le répertoire du projet
pip install -e .
```

### Option 2 : Installation normale

```bash
pip install .
```

## Configuration

### 1. Obtenir une clé API Groq

1. Visitez [https://console.groq.com/](https://console.groq.com/)
2. Créez un compte ou connectez-vous
3. Générez une clé API depuis le tableau de bord

### 2. Configurer la clé API

**Option A : Variable d'environnement (recommandé)**

```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="votre_cle_api_ici"

# Windows (CMD)
set GROQ_API_KEY=votre_cle_api_ici

# Linux/Mac
export GROQ_API_KEY="votre_cle_api_ici"
```

**Option B : Argument de ligne de commande**

```bash
auto_debug script.py --api-key "votre_cle_api"
```

## Utilisation

### Commande de base

```bash
auto_debug script.py
```

### Exemples d'utilisation

```bash
# Avec environnement virtuel spécifique
auto_debug script.py --venv ./venv

# Mode automatique (sans confirmation)
auto_debug script.py --auto

# Limiter le nombre d'itérations
auto_debug script.py --max-iterations 5

# Changer le timeout
auto_debug script.py --timeout 60

# Toutes les options combinées
auto_debug script.py --venv ./venv --max-iterations 3 --auto --timeout 45
```

### Options disponibles

```
positional arguments:
  script                Chemin du script Python à déboguer

optional arguments:
  --api-key KEY         Clé API Groq (ou variable GROQ_API_KEY)
  --venv PATH           Chemin du dossier venv à utiliser
  --max-iterations N    Nombre max d'itérations (défaut: 3)
  --timeout SECONDS     Timeout d'exécution en secondes (défaut: 30)
  --auto                Mode automatique (pas de confirmation)
  -h, --help            Affiche l'aide
```

## Exemple complet

```bash
# 1. Créer un script Python avec une erreur
cat > test.py << EOF
def hello():
    print("Hello, World!")
    print(undefined_variable)  # Erreur intentionnelle

hello()
EOF

# 2. Exécuter auto_debug
auto_debug test.py --auto

# 3. Le script sera automatiquement corrigé !
```

## Vérification de l'installation

Pour vérifier que la commande est bien installée :

```bash
auto_debug --help
```

Vous devriez voir l'aide de la commande s'afficher.

## Désinstallation

```bash
pip uninstall auto-debug
```

## Dépannage

### La commande `auto_debug` n'est pas trouvée

1. Vérifiez que pip a installé dans le bon environnement :
   ```bash
   pip show auto-debug
   ```

2. Vérifiez que le répertoire Scripts (Windows) ou bin (Linux/Mac) est dans votre PATH

3. Réinstallez :
   ```bash
   pip uninstall auto-debug
   pip install -e .
   ```

### Erreur "Clé API Groq requise"

Assurez-vous d'avoir défini la variable d'environnement `GROQ_API_KEY` ou utilisez l'option `--api-key`.

### Erreur lors de l'exécution du script

Vérifiez que :
- Le chemin du script est correct
- Le script est un fichier Python valide
- Les permissions d'exécution sont correctes

