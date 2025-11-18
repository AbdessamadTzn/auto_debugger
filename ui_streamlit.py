"""
Interface Streamlit pour Auto-Debug
"""
import streamlit as st
import sys
from pathlib import Path
from executor import ScriptExecutor
from ai_agent import GrokAgent
from patcher import CodePatcher
import config


def main():
    st.set_page_config(
        page_title="🐞 Auto-Debug",
        page_icon="🐞",
        layout="wide"
    )
    
    st.title("🐞 Auto-Debug - Débogage Intelligent Python")
    st.markdown("*Propulsé par Grok AI*")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Chemin du script
        script_path = st.text_input(
            "📄 Chemin du script Python",
            value=st.session_state.get('script_path', ''),
            placeholder="/chemin/vers/script.py"
        )
        
        # Environnement virtuel
        venv_path = st.text_input(
            "🐍 Environnement virtuel (optionnel)",
            value=st.session_state.get('venv_path', ''),
            placeholder="/chemin/vers/venv"
        )
        
        # API Key
        # API Key
        api_key = st.text_input(
        "Clé API Groq",
            value=config.GROQ_API_KEY,
            type="password",
            help="Ou définissez GROQ_API_KEY dans .env"
        )

        
        analyze_button = st.button("🚀 Analyser le script", type="primary", use_container_width=True)
    
    # Zone principale
    if analyze_button:
        if not script_path:
            st.error("❌ Veuillez spécifier un chemin de script")
            return
        
        if not Path(script_path).exists():
            st.error(f"❌ Fichier introuvable : {script_path}")
            return
        
        # Sauvegarder dans la session
        st.session_state['script_path'] = script_path
        st.session_state['venv_path'] = venv_path
        
        # Exécution du script
        st.header("1️⃣ Exécution du script")
        
        with st.spinner("🐍 Exécution en cours..."):
            executor = ScriptExecutor(venv_path if venv_path else None)
            success, stdout, stderr, returncode = executor.execute(script_path)
        
        if success:
            st.success("✅ Le script s'exécute sans erreur !")
            with st.expander("📄 Sortie standard"):
                st.code(stdout, language="text")
            return
        
        # Afficher l'erreur
        st.error("❌ Erreur détectée !")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Sortie standard")
            st.code(stdout if stdout else "Aucune sortie", language="text")
        
        with col2:
            st.subheader("🔴 Erreur")
            st.code(stderr, language="text")
        
        # Parser l'erreur
        error_info = executor.parse_error(stderr)
        
        with st.expander("🔍 Détails de l'erreur"):
            st.json(error_info)
        
        # Analyse par Grok
        st.header("2️⃣ Analyse par Grok AI")
        
        with st.spinner("🤖 Grok analyse le code..."):
            try:
                agent = GrokAgent(api_key if api_key else None)
                analysis = agent.analyze_error(script_path, error_info)
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
                return
        
        if not analysis:
            st.error("❌ Impossible d'obtenir une analyse de Grok")
            return
        
        # Sauvegarder l'analyse
        st.session_state['analysis'] = analysis
        st.session_state['current_script'] = script_path
        
        # Afficher l'analyse
        display_analysis(analysis)
    
    # Afficher l'analyse précédente si elle existe
    elif 'analysis' in st.session_state:
        st.header("2️⃣ Analyse par Grok AI")
        display_analysis(st.session_state['analysis'])


def display_analysis(analysis: dict):
    """Affiche l'analyse de Grok et permet d'appliquer les corrections"""
    
    # Vérifier si fixable
    if not analysis['fixable']:
        st.warning("⚠️ Cette erreur n'est pas corrigeable automatiquement")
        st.info(f"**Explication :** {analysis['explanation']}")
        return
    
    # Afficher l'explication pédagogique
    st.success("✅ Erreur analysée avec succès !")
    
    st.subheader("📚 Explication pédagogique")
    st.info(analysis['explanation'])
    
    st.subheader("🔧 Corrections proposées")
    
    # Afficher chaque correction
    for i, fix in enumerate(analysis['fixes'], 1):
        with st.expander(f"🔹 Correction {i} - Ligne {fix['line_to_remove']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**❌ Ligne à supprimer**")
                st.code(f"Ligne {fix['line_to_remove']}", language="python")
            
            with col2:
                st.markdown("**✅ Ligne à ajouter**")
                st.code(fix['line_to_add'], language="python")
            
            st.markdown(f"**💡 Raison :** {fix['reason']}")
    
    # Bouton pour appliquer les corrections
    st.divider()
    st.header("3️⃣ Application des corrections")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.warning("⚠️ Les corrections seront appliquées directement sur le fichier source. Un backup sera créé.")
    
    with col2:
        apply_button = st.button("✅ Appliquer les corrections", type="primary", use_container_width=True)
    
    if apply_button:
        script_path = st.session_state.get('current_script')
        if not script_path:
            st.error("❌ Chemin du script introuvable")
            return
        
        with st.spinner("🔧 Application des corrections..."):
            patcher = CodePatcher()
            success = patcher.apply_fixes(analysis['fixes'], Path(script_path).parent)
        
        if success:
            st.success("✅ Corrections appliquées avec succès !")
            st.balloons()
            
            # Proposer de ré-exécuter
            if st.button("🔄 Ré-exécuter le script"):
                st.session_state.pop('analysis', None)
                st.rerun()
        else:
            st.error("❌ Échec de l'application des corrections")


if __name__ == "__main__":
    main()