# app.py (avec intégration Speech-to-Text)

import streamlit as st
from questions_db import (
    get_categories,
    get_available_difficulties,
    get_random_question,
    QUESTIONS_DATABASE_BY_CATEGORY
)
from utils import get_llm_feedback, transcribe_audio_from_mic # Ajout de transcribe_audio_from_mic

# Configuration de la page Streamlit
st.set_page_config(page_title="Simulateur d'Entretien IA", layout="wide")

# --- FONCTION POUR CHARGER LE CSS PERSONNALISÉ ---
def load_custom_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Charger le CSS personnalisé
load_custom_css("assets/style.css")

def streamlit_status_update(message: str, type: str = "info"):
    """Fonction pour afficher les mises à jour de statut dans Streamlit."""
    if type == "info":
        st.info(message, icon="🎤")
    elif type == "warning":
        st.warning(message, icon="⚠️")
    elif type == "error":
        st.error(message, icon="🚨")
    elif type == "success":
        st.success(message, icon="✅")
    # Vous pouvez utiliser un st.status pour des messages qui se mettent à jour
    # Exemple:
    # with st.status("Enregistrement...", expanded=True) as status_container:
    #     status_container.update(label=message)
    # Mais pour des messages simples, st.info/warning/etc. sont bien.


def initialize_session_state():
    """Initialise les variables de l'état de session si elles n'existent pas."""
    if "available_categories" not in st.session_state:
        st.session_state.available_categories = get_categories()

    if "selected_category" not in st.session_state:
        st.session_state.selected_category = st.session_state.available_categories[0] if st.session_state.available_categories else None

    if "available_difficulties_for_category" not in st.session_state:
        if st.session_state.selected_category:
            st.session_state.available_difficulties_for_category = get_available_difficulties(st.session_state.selected_category)
        else:
            st.session_state.available_difficulties_for_category = []

    if "selected_difficulty" not in st.session_state:
        st.session_state.selected_difficulty = st.session_state.available_difficulties_for_category[0] if st.session_state.available_difficulties_for_category else None

    if "current_question_data" not in st.session_state:
        st.session_state.current_question_data = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "user_answer" not in st.session_state: # Texte de la réponse, qu'il soit tapé ou transcrit
        st.session_state.user_answer = ""
    if "question_key_counter" not in st.session_state:
        st.session_state.question_key_counter = 0
    if "criteria_of_current_question" not in st.session_state:
        st.session_state.criteria_of_current_question = (None, None)
    if "is_recording" not in st.session_state: # Pour gérer l'état de l'enregistrement
        st.session_state.is_recording = False
    if "transcription_message" not in st.session_state: # Pour afficher les messages de transcription
        st.session_state.transcription_message = ""
    if "transcription_message_type" not in st.session_state:
        st.session_state.transcription_message_type = "info"


def load_new_question(category_name: str | None, difficulty_level: str | None):
    if not category_name or not difficulty_level:
        st.session_state.current_question_data = None
        st.session_state.criteria_of_current_question = (category_name, difficulty_level)
        return

    new_question = get_random_question(category_name, difficulty_level)
    if new_question:
        st.session_state.current_question_data = new_question
    else:
        st.session_state.current_question_data = None
        st.warning(f"Aucune question disponible pour '{category_name}' - '{difficulty_level}'.", icon="🤷")

    st.session_state.criteria_of_current_question = (category_name, difficulty_level)
    st.session_state.feedback = None
    st.session_state.user_answer = "" # Effacer la réponse précédente
    st.session_state.transcription_message = "" # Effacer les messages de transcription
    st.session_state.question_key_counter += 1


# --- Initialisation ---
initialize_session_state()

# --- Interface Utilisateur ---
st.title("🎙️ Simulateur d'Entretien IA avec Voix")
st.markdown("Répondez aux questions à l'écrit ou **à l'oral** !")
st.divider()

# --- Sélection de Catégorie et Difficulté (inchangé) ---
if not st.session_state.available_categories:
    st.error("Aucune catégorie trouvée. Vérifiez `questions_db.py`.", icon="🚫")
    st.stop()
col_select1, col_select2 = st.columns(2)
with col_select1:
    default_cat_index = 0
    if st.session_state.selected_category and st.session_state.selected_category in st.session_state.available_categories:
        default_cat_index = st.session_state.available_categories.index(st.session_state.selected_category)
    newly_selected_category = st.selectbox(
        "1. Choisissez une catégorie :", options=st.session_state.available_categories,
        index=default_cat_index, key="category_selector"
    )
with col_select2:
    if newly_selected_category != st.session_state.selected_category:
        st.session_state.selected_category = newly_selected_category
        st.session_state.available_difficulties_for_category = get_available_difficulties(st.session_state.selected_category)
        st.session_state.selected_difficulty = st.session_state.available_difficulties_for_category[0] if st.session_state.available_difficulties_for_category else None
        st.session_state.current_question_data = None; st.session_state.feedback = None; st.session_state.user_answer = ""; st.session_state.criteria_of_current_question = (None, None)
        st.rerun()
    default_diff_index = 0
    if st.session_state.selected_difficulty and st.session_state.selected_difficulty in st.session_state.available_difficulties_for_category:
        default_diff_index = st.session_state.available_difficulties_for_category.index(st.session_state.selected_difficulty)
    elif st.session_state.available_difficulties_for_category:
        st.session_state.selected_difficulty = st.session_state.available_difficulties_for_category[0]; default_diff_index = 0
    newly_selected_difficulty = st.selectbox(
        "2. Choisissez une difficulté :", options=st.session_state.available_difficulties_for_category,
        index=default_diff_index, key="difficulty_selector",
        disabled=not st.session_state.available_difficulties_for_category
    )
if newly_selected_difficulty != st.session_state.selected_difficulty:
    st.session_state.selected_difficulty = newly_selected_difficulty
    st.session_state.current_question_data = None; st.session_state.feedback = None; st.session_state.user_answer = ""; st.session_state.criteria_of_current_question = (None, None)
    st.rerun()

current_criteria = (st.session_state.selected_category, st.session_state.selected_difficulty)
if st.session_state.current_question_data is None or st.session_state.criteria_of_current_question != current_criteria:
    if st.session_state.selected_category and st.session_state.selected_difficulty:
        load_new_question(st.session_state.selected_category, st.session_state.selected_difficulty)

st.divider()
col_question, col_feedback = st.columns(2, gap="large")

with col_question:
    display_cat = st.session_state.selected_category or "N/A"
    display_diff = st.session_state.selected_difficulty or "N/A"
    st.subheader(f"🎯 Question ({display_cat} - {display_diff})")

    disabled_new_question_button = not (st.session_state.selected_category and st.session_state.selected_difficulty)
    if st.button("🔄 Nouvelle Question (mêmes critères)", key="new_question_button_criteria", disabled=disabled_new_question_button):
        load_new_question(st.session_state.selected_category, st.session_state.selected_difficulty)
        st.rerun()

    if st.session_state.current_question_data and \
       st.session_state.criteria_of_current_question == current_criteria:
        question_id = st.session_state.current_question_data["id"]
        question_text = st.session_state.current_question_data["text"]
        st.info(f"**ID: {question_id}**\n\n{question_text}")

        # --- Section Réponse Utilisateur avec Speech-to-Text ---
        st.write("#### Votre Réponse :")

        # Conteneur pour les messages de transcription
        transcription_status_placeholder = st.empty()

        if st.session_state.transcription_message:
            if st.session_state.transcription_message_type == "info":
                transcription_status_placeholder.info(st.session_state.transcription_message, icon="🎤")
            elif st.session_state.transcription_message_type == "warning":
                transcription_status_placeholder.warning(st.session_state.transcription_message, icon="⚠️")
            elif st.session_state.transcription_message_type == "error":
                transcription_status_placeholder.error(st.session_state.transcription_message, icon="🚨")
            elif st.session_state.transcription_message_type == "success":
                transcription_status_placeholder.success(st.session_state.transcription_message, icon="✅")


        # Fonction pour mettre à jour le message de transcription dans Streamlit
        def st_transcription_update(message: str):
            # Simple mise à jour de l'état, le rendu se fera au prochain cycle
            if "erreur" in message.lower() or "problème" in message.lower() or "n'a pas pu" in message.lower():
                st.session_state.transcription_message_type = "warning"
            elif "réussie" in message.lower() or "transcription en cours" in message.lower():
                 st.session_state.transcription_message_type = "success"
            else: # Par défaut info pour les messages comme "Parlez maintenant"
                 st.session_state.transcription_message_type = "info"
            st.session_state.transcription_message = message
            # Pas de st.rerun() ici pour éviter des re-renderings intempestifs pendant l'écoute.
            # L'affichage du message se mettra à jour quand Streamlit le décidera (ou à la fin de l'opération).
            # Pour une mise à jour plus instantanée, il faudrait utiliser st.status.

        # Bouton pour démarrer la transcription
        # Gérer l'état "is_recording" pour changer le label du bouton pourrait être une amélioration future.
        if st.button("🎙️ Parler ma réponse", key="speak_button", use_container_width=True, disabled=st.session_state.is_recording):
            st.session_state.is_recording = True
            st.session_state.transcription_message = "Initialisation du microphone..."
            st.session_state.transcription_message_type = "info"
            st.rerun() # Pour afficher le message d'initialisation

        if st.session_state.is_recording:
            # Vider le message précédent avant de commencer une nouvelle transcription
            # transcription_status_placeholder.empty() # Ceci enlève le message, ce n'est peut-être pas souhaité
            
            # Nous appelons la fonction de transcription ici, elle utilisera print ou st_transcription_update
            # Pour une meilleure UX, on pourrait encapsuler transcribe_audio_from_mic dans un spinner
            # ou utiliser st.status
            
            # Utilisation de st.status pour un meilleur feedback utilisateur pendant l'enregistrement
            with st.status("Enregistrement et transcription en cours...", expanded=True) as status:
                def update_status_in_spinner(message: str):
                    if "erreur" in message.lower() or "problème" in message.lower() or "n'a pas pu" in message.lower():
                        status.update(label=message, state="error")
                    elif "réussie" in message.lower():
                        status.update(label=message, state="complete")
                    else:
                        status.update(label=message, state="running")
                    st.session_state.transcription_message = message # Garder pour affichage après

                transcribed_text = transcribe_audio_from_mic(status_update_func=update_status_in_spinner)
                
                if not transcribed_text.startswith("ERREUR_"):
                    # Ajouter le texte transcrit à la réponse existante (ou remplacer)
                    # Pour cet exemple, on ajoute avec un espace.
                    if st.session_state.user_answer: # Si du texte existait déjà
                        st.session_state.user_answer += " " + transcribed_text
                    else:
                        st.session_state.user_answer = transcribed_text
                    st.session_state.transcription_message = "Transcription ajoutée à votre réponse."
                    st.session_state.transcription_message_type = "success"
                    status.update(label="Transcription terminée et ajoutée !", state="complete")
                else:
                    # Gérer les messages d'erreur retournés par transcribe_audio_from_mic
                    st.session_state.transcription_message = f"Erreur de transcription : {transcribed_text.replace('ERREUR_', '').replace(':', ' ')}"
                    st.session_state.transcription_message_type = "error"
                    status.update(label=f"Échec de la transcription : {transcribed_text}", state="error")
            
            st.session_state.is_recording = False # Réinitialiser l'état d'enregistrement
            st.rerun() # Rafraîchir pour afficher le texte dans text_area et le message final


        # Zone de texte pour la réponse (toujours présente)
        # La valeur est maintenant gérée par st.session_state.user_answer
        user_answer_input_val = st.text_area(
            "Tapez ou modifiez votre réponse ici :",
            value=st.session_state.user_answer, # Utiliser la valeur de session_state
            height=200,
            key=f"user_answer_input_val_{st.session_state.question_key_counter}", # Clé dynamique
            placeholder="Votre réponse apparaîtra ici après la transcription, ou tapez directement."
        )
        # Mettre à jour st.session_state.user_answer si l'utilisateur tape manuellement
        if user_answer_input_val != st.session_state.user_answer:
            st.session_state.user_answer = user_answer_input_val
            st.session_state.transcription_message = "" # Effacer les messages de transcription si l'utilisateur tape
            st.rerun() # Pour que le message de transcription disparaisse si on tape


        # Bouton de soumission (inchangé en termes de logique de feedback)
        if st.button("✅ Soumettre pour Analyse Complète", key="submit_button_main", type="primary", use_container_width=True):
            st.session_state.transcription_message = "" # Effacer avant soumission
            if not st.session_state.user_answer.strip():
                st.warning("Veuillez fournir une réponse (tapée ou parlée).", icon="⚠️")
            else:
                with st.spinner("🧠 L'IA procède à une analyse approfondie..."):
                    # ... (logique de get_llm_feedback reste la même)
                    try:
                        q_text_for_feedback = st.session_state.current_question_data["text"]
                        cat_for_feedback = st.session_state.selected_category
                        feedback_text = get_llm_feedback(q_text_for_feedback, st.session_state.user_answer, cat_for_feedback)
                        st.session_state.feedback = feedback_text
                        # ... (gestion des erreurs de feedback)
                    except Exception as e:
                        st.error(f"Erreur de communication avec l'IA : {e}", icon="🚨")
                        st.session_state.feedback = "Erreur lors de l'obtention du feedback."
                        
    # ... (Reste de la colonne question si des messages d'erreur sont nécessaires)
    elif st.session_state.selected_category and st.session_state.selected_difficulty and \
         (st.session_state.current_question_data is None and st.session_state.criteria_of_current_question == current_criteria) :
        st.info("Prêt pour une nouvelle question. Ajustez les sélections si besoin.", icon="🧐")
    elif not st.session_state.selected_category or not st.session_state.selected_difficulty:
        st.info("Veuillez sélectionner une catégorie ET une difficulté pour commencer.", icon="👈")


# --- Section d'affichage du Feedback (inchangée) ---
with col_feedback:
    st.subheader("🔍 Analyse IA de Votre Réponse")
    if st.session_state.feedback:
        st.markdown(st.session_state.feedback)
    else:
        st.info("Soumettez votre réponse pour recevoir une analyse détaillée.", icon="💬")

st.divider()
st.caption(f"Simulateur v0.6 - Speech-to-Text | Catégories: {len(st.session_state.available_categories)}")