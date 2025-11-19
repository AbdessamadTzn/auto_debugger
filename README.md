# 🐍 Agent de Debugging Python Automatique

Un outil modulaire pour déboguer automatiquement des scripts Python en utilisant l'intelligence artificielle via l'API Groq.

## 📋 Description

L'Agent de Debugging Python Automatique est un outil qui :
1. Exécute un script Python dans son environnement virtuel
2. Capture les erreurs (traceback) lors de l'exécution
3. Analyse l'erreur avec l'API Groq pour obtenir des corrections
4. Applique automatiquement les corrections au fichier source
5. Fournit une interface utilisateur simple avec Streamlit

## 🏗️ Structure du Projet

```
auto_debugger/
├── config.py          # Gestion de la configuration
├── executor.py         # Exécution du script et capture d'erreurs
├── llm_analyzer.py     # Interface avec l'API Groq
├── patcher.py          # Application des corrections
├── app.py              # Interface Streamlit principale
├── requirements.txt    # Dépendances Python
└── README.md           # Documentation du projet
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Un environnement virtuel Python (venv, virtualenv, etc.)

### Installation des dépendances

1. Clonez ou téléchargez ce projet
2. Créez un environnement virtuel (si ce n'est pas déjà fait) :
   ```bash
   python -m venv venv
   ```

3. Activez l'environnement virtuel :
   - Sur Windows :
     ```bash
     venv\Scripts\activate
     ```
   - Sur Linux/Mac :
     ```bash
     source venv/bin/activate
     ```

4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Utilisation

### Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`

### Configuration

1. Dans la barre latérale de l'application :
   - **Chemin du projet** : Entrez le chemin absolu vers votre projet Python
   - **Nom de l'environnement virtuel** : Entrez le nom du dossier de votre venv (ex: `venv`, `.venv`)
   - **Script à déboguer** : Entrez le chemin relatif du script depuis le répertoire du projet (ex: `main.py`, `src/app.py`)
   - **Clé API Groq** : Entrez votre clé API Groq (ou définissez `GROQ_API_KEY` dans l'environnement)

2. Cliquez sur "💾 Sauvegarder la configuration" pour enregistrer vos paramètres

### Débogage

1. Cliquez sur "🚀 Exécuter et Déboguer"
2. Si une erreur est détectée :
   - Le traceback sera affiché
   - L'IA analysera l'erreur et proposera des corrections
   - Vous pourrez prévisualiser les corrections avant de les appliquer
3. Cliquez sur "✅ Appliquer les Corrections" pour modifier le fichier source
4. Une sauvegarde automatique sera créée avant toute modification

## 📝 Format des Corrections

Les corrections sont au format JSON strict :

```json
{
  "file": "file_to_correct.py",
  "corrections": [
    {
      "action": "replace",
      "line_number": 12,
      "new_content": "nouvelle ligne de code"
    },
    {
      "action": "insert",
      "line_number": 15,
      "new_content": "ligne à insérer"
    },
    {
      "action": "delete",
      "line_number": 20
    }
  ]
}
```

### Types d'actions

- **`replace`** : Remplace une ligne existante
- **`insert`** : Insère une nouvelle ligne après la ligne spécifiée
- **`delete`** : Supprime une ligne

## 🔧 Modules

### `config.py`
Gère la configuration du projet (chemins, environnement virtuel, script cible).

### `executor.py`
Exécute le script Python et capture les erreurs avec `subprocess`.

### `llm_analyzer.py`
Utilise l'**API Groq** pour analyser les erreurs et proposer des corrections. 
- Configurez votre clé API Groq via la variable d'environnement `GROQ_API_KEY` ou dans l'interface Streamlit

### `patcher.py`
Applique les corrections au fichier source selon le format JSON.

### `app.py`
Interface utilisateur Streamlit pour configurer et utiliser l'outil.

## 🔑 Configuration de l'API Groq

### Obtenir une clé API Groq

1. Visitez [https://console.groq.com/](https://console.groq.com/)
2. Créez un compte ou connectez-vous
3. Générez une clé API depuis le tableau de bord

### Configurer la clé API

**Option 1 : Variable d'environnement (recommandé)**
```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="votre_cle_api_ici"

# Windows (CMD)
set GROQ_API_KEY=votre_cle_api_ici

# Linux/Mac
export GROQ_API_KEY="votre_cle_api_ici"
```

**Option 2 : Interface Streamlit**
- Lancez l'application avec `streamlit run app.py`
- Dans la barre latérale, section "🤖 API Groq", entrez votre clé API
- Sélectionnez le modèle Groq souhaité (par défaut: `llama3-8b-8192`)

### Modèles disponibles

- `llama3-8b-8192` (défaut) - Rapide et efficace
- `llama3-70b-8192` - Plus puissant
- `mixtral-8x7b-32768` - Très performant
- `gemma-7b-it` - Modèle Google

## 📦 Sauvegarde Automatique

Avant d'appliquer des corrections, une sauvegarde du fichier original est créée automatiquement avec un timestamp :
- Format : `nom_fichier_backup_YYYYMMDD_HHMMSS.py`

## ⚠️ Limitations

- **L'API Groq est obligatoire** - aucune analyse ne peut être effectuée sans une clé API valide
- L'API Groq nécessite une connexion Internet
- Les corrections proposées par l'IA doivent être vérifiées avant application
- Les erreurs de l'API Groq (quota dépassé, clé invalide, etc.) empêcheront l'analyse

## 🛠️ Développement

### Structure Modulaire

Le projet est conçu de manière modulaire pour faciliter :
- L'extension des fonctionnalités
- Le remplacement de l'API Groq par une autre API si nécessaire
- L'ajout de nouveaux types de corrections
- Les tests unitaires

## 📄 Licence

Ce projet est fourni tel quel pour usage éducatif et de développement.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

