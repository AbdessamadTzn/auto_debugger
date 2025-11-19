"""
Interface Streamlit principale pour l'Agent de Debugging Python Automatique.
"""

import streamlit as st
import os
import json
from config import Config
from executor import execute_script, read_source_code
from llm_analyzer import analyze_error, validate_correction_json
from patcher import apply_corrections, preview_corrections


# Configuration de la page Streamlit
st.set_page_config(
    page_title="Auto Debugger Python",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Agent de Debugging Python Automatique")
st.markdown("---")

# Initialise la session state
if 'config' not in st.session_state:
    st.session_state.config = Config()
if 'execution_result' not in st.session_state:
    st.session_state.execution_result = None
if 'corrections' not in st.session_state:
    st.session_state.corrections = None
if 'source_code' not in st.session_state:
    st.session_state.source_code = None
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")
if 'groq_model' not in st.session_state:
    st.session_state.groq_model = "llama3-8b-8192"


# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Chemin du projet
    project_path = st.text_input(
        "Chemin du projet",
        value=st.session_state.config.project_path or "",
        help="Chemin absolu vers le répertoire du projet"
    )
    
    if project_path and project_path != st.session_state.config.project_path:
        try:
            st.session_state.config.set_project_path(project_path)
            st.success("Chemin du projet défini")
        except ValueError as e:
            st.error(str(e))
    
    # Nom de l'environnement virtuel
    venv_name = st.text_input(
        "Nom de l'environnement virtuel",
        value=st.session_state.config.venv_name or "venv",
        help="Nom du dossier de l'environnement virtuel (ex: venv, .venv)"
    )
    
    if venv_name:
        st.session_state.config.set_venv_name(venv_name)
    
    # Script cible
    if st.session_state.config.project_path:
        target_script = st.text_input(
            "Script à déboguer",
            value=st.session_state.config.target_script or "",
            help="Chemin relatif du script depuis le répertoire du projet"
        )
        
        if target_script and target_script != st.session_state.config.target_script:
            try:
                st.session_state.config.set_target_script(target_script)
                st.success("Script cible défini")
            except ValueError as e:
                st.error(str(e))
    
    st.markdown("---")
    
    # Configuration API Groq
    st.header("🤖 API Groq")
    
    groq_api_key = st.text_input(
        "Clé API Groq",
        value=st.session_state.groq_api_key,
        type="password",
        help="Clé API Groq (ou définissez GROQ_API_KEY dans l'environnement)"
    )
    
    if groq_api_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = groq_api_key
        if groq_api_key:
            st.success("Clé API Groq définie")
    
    model_options = ["openai/gpt-oss-20b", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
    try:
        current_index = model_options.index(st.session_state.groq_model)
    except ValueError:
        current_index = 0
    
    groq_model = st.selectbox(
        "Modèle Groq",
        options=model_options,
        index=current_index,
        help="Modèle Groq à utiliser pour l'analyse"
    )
    
    if groq_model != st.session_state.groq_model:
        st.session_state.groq_model = groq_model
    
    st.markdown("---")
    
    # Bouton pour sauvegarder la configuration
    if st.button("💾 Sauvegarder la configuration"):
        try:
            st.session_state.config.save()
            st.success("Configuration sauvegardée!")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde: {str(e)}")


# Zone principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Exécution et Débogage")
    
    # Vérifie que la configuration est valide
    if not st.session_state.config.is_valid():
        st.warning("⚠️ Veuillez configurer le projet, l'environnement virtuel et le script cible dans la barre latérale.")
    else:
        # Affiche les informations de configuration
        with st.expander("📋 Configuration actuelle", expanded=False):
            st.json(st.session_state.config.to_dict())
        
        # Bouton pour exécuter le script
        if st.button("🚀 Exécuter et Déboguer", type="primary"):
            with st.spinner("Exécution du script en cours..."):
                python_exe = st.session_state.config.get_venv_python()
                script_path = st.session_state.config.get_target_script_path()
                
                # Exécute le script
                result = execute_script(
                    python_exe,
                    script_path,
                    st.session_state.config.project_path
                )
                
                st.session_state.execution_result = result
                
                # Lit le code source
                st.session_state.source_code = read_source_code(script_path)
                
                # Si erreur, analyse avec le LLM Groq
                if not result['success']:
                    with st.spinner("Analyse de l'erreur avec l'IA (Groq)..."):
                        try:
                            corrections_data = analyze_error(
                                st.session_state.source_code,
                                result['traceback'] or result['stderr'],
                                os.path.basename(script_path),
                                api_key=st.session_state.groq_api_key if st.session_state.groq_api_key else None,
                                model=st.session_state.groq_model
                            )
                            st.session_state.corrections = corrections_data
                        except ImportError as e:
                            st.error(f"❌ Erreur: {str(e)}")
                            st.info("💡 Installez le package groq avec: `pip install groq`")
                        except ValueError as e:
                            st.error(f"❌ Erreur de configuration: {str(e)}")
                            st.info("💡 Configurez votre clé API Groq dans la barre latérale ou via la variable d'environnement GROQ_API_KEY")
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'appel à l'API Groq: {str(e)}")
                            st.info("💡 Vérifiez votre clé API et votre connexion Internet")
        
        # Affiche le résultat de l'exécution
        if st.session_state.execution_result:
            result = st.session_state.execution_result
            
            if result['success']:
                st.success("✅ Script exécuté avec succès!")
                if result['stdout']:
                    st.text_area("Sortie standard", result['stdout'], height=200)
            else:
                st.error("❌ Erreur détectée lors de l'exécution")
                
                # Affiche le traceback
                if result['traceback']:
                    st.text_area("Traceback", result['traceback'], height=200)
                elif result['stderr']:
                    st.text_area("Erreur", result['stderr'], height=200)
        
        # Affiche les corrections proposées
        if st.session_state.corrections:
            st.markdown("---")
            st.header("🔧 Corrections Proposées")
            
            # Valide le format JSON
            if validate_correction_json(st.session_state.corrections):
                st.success("Format JSON valide")
                
                # Affiche les corrections
                corrections = st.session_state.corrections.get("corrections", [])
                st.write(f"**{len(corrections)} correction(s) proposée(s)**")
                
                # Prévisualisation des corrections
                script_path = st.session_state.config.get_target_script_path()
                preview = preview_corrections(script_path, st.session_state.corrections)
                
                for i, preview_line in enumerate(preview, 1):
                    st.code(preview_line, language=None)
                
                # Bouton pour appliquer les corrections
                col_apply1, col_apply2 = st.columns([1, 1])
                
                with col_apply1:
                    if st.button("✅ Appliquer les Corrections", type="primary"):
                        script_path = st.session_state.config.get_target_script_path()
                        result = apply_corrections(script_path, st.session_state.corrections)
                        
                        if result['success']:
                            st.success(result['message'])
                            if result['backup_path']:
                                st.info(f"📦 Sauvegarde créée: {os.path.basename(result['backup_path'])}")
                            # Réinitialise pour permettre une nouvelle exécution
                            st.session_state.execution_result = None
                            st.session_state.corrections = None
                            st.rerun()
                        else:
                            st.error(result['message'])
                
                with col_apply2:
                    if st.button("🔄 Réinitialiser"):
                        st.session_state.execution_result = None
                        st.session_state.corrections = None
                        st.rerun()
                
                # Affiche le JSON brut
                with st.expander("📄 JSON des Corrections"):
                    st.json(st.session_state.corrections)
            else:
                st.error("Format JSON invalide")

with col2:
    st.header("📚 Informations")
    
    st.markdown("""
    ### Comment utiliser:
    
    1. **Configurez** le projet dans la barre latérale:
       - Chemin du projet
       - Nom de l'environnement virtuel
       - Script à déboguer
    
    2. **Exécutez** le script avec le bouton "Exécuter et Déboguer"
    
    3. Si une erreur est détectée, l'IA analysera le code et proposera des corrections
    
    4. **Appliquez** les corrections proposées
    
    ### Format des corrections:
    
    Les corrections sont au format JSON strict:
    - `replace`: Remplace une ligne
    - `insert`: Insère une nouvelle ligne
    - `delete`: Supprime une ligne
    
    ### API Groq:
    
    Cette version utilise l'**API Groq** pour l'analyse des erreurs.
    Configurez votre clé API Groq dans la barre latérale.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Agent de Debugging Python Automatique - Version 1.0</div>",
    unsafe_allow_html=True
)

