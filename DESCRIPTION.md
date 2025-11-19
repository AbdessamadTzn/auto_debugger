# 🐍 Auto Debugger - Agent de Debugging Python Automatique

## Vue d'ensemble

**Auto Debugger** est un outil intelligent et modulaire conçu pour déboguer automatiquement des scripts Python en utilisant l'intelligence artificielle. Il combine l'exécution automatisée de scripts, la capture d'erreurs, l'analyse par IA via l'API Groq, et l'application automatique de corrections dans une interface utilisateur intuitive basée sur Streamlit.

## 🎯 Objectif

L'objectif principal de cet outil est de réduire le temps passé sur le débogage manuel en automatisant le processus de détection, d'analyse et de correction des erreurs Python. Il permet aux développeurs de se concentrer sur la logique métier plutôt que sur la résolution de bugs syntaxiques ou d'erreurs courantes.

## ✨ Fonctionnalités principales

### 1. Exécution automatisée
- Exécute des scripts Python dans leur environnement virtuel dédié
- Capture la sortie standard (stdout) et les erreurs (stderr)
- Extrait automatiquement les tracebacks pour une analyse précise
- Gère les timeouts et les erreurs d'exécution

### 2. Analyse intelligente par IA
- Utilise l'API Groq avec plusieurs modèles disponibles 
- Analyse le code source et les erreurs pour proposer des corrections précises et un explication de l'erreur
- Génère des corrections au format JSON structuré

### 3. Application automatique de corrections
- Applique trois types de corrections :
  - **Replace** : Remplace une ligne existante
  - **Insert** : Insère une nouvelle ligne après une ligne spécifiée
  - **Delete** : Supprime une ligne problématique
- Crée automatiquement une sauvegarde avant toute modification
- Prévisualise les corrections avant application

### 4. Interface utilisateur intuitive
- Interface web moderne avec Streamlit
- Configuration simple via la barre latérale
- Affichage en temps réel des résultats d'exécution
- Prévisualisation des corrections proposées
- Gestion de la configuration persistante

## 🏗️ Architecture

Le projet suit une architecture modulaire claire :

```
auto_debugger/
├── config.py          # Gestion de la configuration (chemins, venv, script cible)
├── executor.py         # Exécution du script et capture d'erreurs
├── llm_analyzer.py     # Interface avec l'API Groq pour l'analyse IA
├── patcher.py          # Application des corrections au fichier source
├── app.py              # Interface Streamlit principale
├── requirements.txt    # Dépendances Python
└── README.md           # Documentation complète
```

### Modules détaillés

#### `config.py`
- Gère la configuration du projet (chemins absolus, environnement virtuel)
- Validation des chemins et des fichiers
- Sauvegarde/chargement de la configuration en JSON
- Détection automatique de l'exécutable Python dans le venv

#### `executor.py`
- Exécution sécurisée de scripts via `subprocess`
- Capture de stdout, stderr et codes de retour
- Extraction intelligente des tracebacks
- Gestion des timeouts et erreurs d'exécution

#### `llm_analyzer.py`
- Intégration avec l'API Groq
- Construction de prompts optimisés pour l'analyse d'erreurs
- Validation du format JSON des corrections
- Extraction robuste de JSON depuis les réponses de l'IA

#### `patcher.py`
- Application des corrections selon le format JSON strict
- Tri intelligent des corrections pour éviter les décalages de lignes
- Création automatique de sauvegardes avec timestamp
- Prévisualisation des modifications avant application

#### `app.py`
- Interface Streamlit complète
- Gestion de l'état de session
- Configuration interactive
- Affichage des résultats et corrections

## 🔄 Flux de travail

1. **Configuration** : L'utilisateur configure le projet, l'environnement virtuel et le script cible
2. **Exécution** : Le script est exécuté dans son environnement virtuel
3. **Détection** : Si une erreur survient, elle est capturée avec son traceback complet
4. **Analyse** : L'IA analyse le code source et l'erreur pour identifier la cause
5. **Correction** : L'IA propose des corrections au format JSON structuré
6. **Prévisualisation** : L'utilisateur peut prévisualiser les corrections proposées
7. **Application** : Les corrections sont appliquées automatiquement avec sauvegarde

## 🛠️ Technologies utilisées

- **Python 3.8+** : Langage de programmation principal
- **Streamlit** : Framework pour l'interface utilisateur web
- **Groq API** : Service d'IA pour l'analyse et les corrections
- **subprocess** : Exécution sécurisée des scripts Python
- **JSON** : Format de communication pour les corrections

## 📋 Prérequis

- Python 3.8 ou supérieur
- Un environnement virtuel Python (venv, virtualenv, etc.)
- Une clé API Groq (gratuite, disponible sur [console.groq.com](https://console.groq.com/))
- Connexion Internet (pour l'API Groq)

## 🚀 Installation rapide

```bash
# 1. Cloner le projet
git clone <repository-url>
cd auto_debugger

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer la clé API Groq (optionnel)
export GROQ_API_KEY="votre_cle_api"

# 6. Lancer l'application
streamlit run app.py
```

## 💡 Cas d'usage

- **Débogage rapide** : Corriger rapidement les erreurs de syntaxe et les bugs courants
- **Apprentissage** : Comprendre les erreurs Python grâce aux explications de l'IA
- **Développement itératif** : Tester et corriger rapidement pendant le développement
- **Code legacy** : Moderniser et corriger du code existant
- **Formation** : Enseigner le débogage Python avec des exemples concrets

## ⚠️ Limitations

- Nécessite une connexion Internet pour l'API Groq
- Les corrections proposées doivent être vérifiées par l'utilisateur
- Limité aux erreurs détectables lors de l'exécution
- Dépend des quotas et limites de l'API Groq
- Fonctionne uniquement avec des scripts Python autonomes

## 🔒 Sécurité

- Les sauvegardes automatiques protègent contre la perte de code
- Validation stricte du format JSON des corrections
- Vérification des chemins de fichiers avant modification
- Gestion sécurisée des clés API (variables d'environnement recommandées)

## 📈 Améliorations futures possibles

- Support de plusieurs fichiers simultanés
- Intégration avec d'autres APIs d'IA (OpenAI, Anthropic, etc.)
- Mode batch pour traiter plusieurs scripts
- Historique des corrections appliquées
- Support des tests unitaires
- Intégration avec des IDE populaires (VSCode, PyCharm)

## 📄 Licence

Ce projet est fourni tel quel pour usage éducatif et de développement.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug ou proposer une fonctionnalité
- Soumettre une pull request avec vos améliorations
- Améliorer la documentation

---

**Développé avec ❤️ pour faciliter le débogage Python**

