# Installation d'Auto Debug

## Installation en mode développement

Pour installer `auto_debug` comme commande système en mode développement :

```bash
# Depuis le répertoire du projet
pip install -e .
```

Cela installera la commande `auto_debug` de manière à ce que les modifications du code soient immédiatement reflétées.

## Installation normale

Pour installer depuis le répertoire local :

```bash
pip install .
```

## Installation depuis PyPI (si publié)

```bash
pip install auto-debug
```

## Utilisation

Une fois installé, vous pouvez utiliser la commande directement :

```bash
# Avec clé API en variable d'environnement
export GROQ_API_KEY="votre_cle_api"
auto_debug script.py

# Avec clé API en argument
auto_debug script.py --api-key "votre_cle_api"

# Avec environnement virtuel
auto_debug script.py --venv ./venv

# Mode automatique (sans confirmation)
auto_debug script.py --auto

# Avec options avancées
auto_debug script.py --max-iterations 5 --timeout 60
```

## Désinstallation

```bash
pip uninstall auto-debug
```

## Vérification de l'installation

Pour vérifier que la commande est bien installée :

```bash
auto_debug --help
```

