# utils.py (version révisée avec gTTS vers BytesIO)

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from prompts_llm import format_user_prompt #, format_follow_up_prompt (et autres si vous les avez)

# Imports pour Speech-to-Text
import speech_recognition as sr

# --- NOUVEAUX IMPORTS POUR TEXT-TO-SPEECH (gTTS) ---
from gtts import gTTS
from io import BytesIO # Pour gérer l'audio en mémoire
# ----------------------------------------------------

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ... (configurations et autres fonctions comme avant) ...
GENERATION_CONFIG_FEEDBACK = { "temperature": 0.6, "top_p": 0.95, "top_k": 40, "max_output_tokens": 1024 }
SAFETY_SETTINGS = [ {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]

def get_llm_feedback(question_text: str, user_answer_text: str, category_name: str) -> str:
    if not GOOGLE_API_KEY: return "Feedback simulé (Clé API manquante)."
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest", generation_config=GENERATION_CONFIG_FEEDBACK, safety_settings=SAFETY_SETTINGS)
        prompt = format_user_prompt(question_text, user_answer_text, category_name)
        if "Erreur:" in prompt: return prompt
        response = model.generate_content(prompt)
        return response.text if response.parts else "Feedback non généré."
    except Exception as e: return f"Erreur LLM: {e}"

def transcribe_audio_from_mic(status_update_func=print) -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            status_update_func("Calibrage du microphone...")
            try: recognizer.adjust_for_ambient_noise(source, duration=1)
            except Exception as e: status_update_func(f"Avertissement calibrage: {e}")
            status_update_func("Parlez maintenant...")
            try: audio_data = recognizer.listen(source, timeout=15, phrase_time_limit=90)
            except sr.WaitTimeoutError: return "ERREUR_TIMEOUT: Aucune parole."
            status_update_func("Transcription...")
            try: return recognizer.recognize_google(audio_data, language='fr-FR')
            except sr.UnknownValueError: return "ERREUR_INCOMPREHENSIBLE: Audio non compris."
            except sr.RequestError as e: return f"ERREUR_SERVICE_GOOGLE: {e}"
    except Exception as e: return f"ERREUR_MICROPHONE: {e}"


# --- NOUVELLE FONCTION POUR TEXT-TO-SPEECH (gTTS vers BytesIO) ---
def generate_audio_feedback_gtts_bytes(text_feedback: str, lang: str = 'fr') -> BytesIO | None:
    """
    Génère des données audio en mémoire à partir du texte du feedback en utilisant gTTS.

    Args:
        text_feedback: Le texte à convertir en parole.
        lang: La langue du texte (par défaut 'fr' pour français).

    Returns:
        Un objet io.BytesIO contenant les données audio MP3, ou None en cas d'erreur.
    """
    if not text_feedback or not text_feedback.strip():
        print("Erreur gTTS: Texte de feedback vide fourni.")
        return None

    try:
        tts = gTTS(text=text_feedback, lang=lang, slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0) # Important: remettre le curseur au début du buffer
        return audio_fp

    except AssertionError as ae:
        print(f"Erreur gTTS (AssertionError): {ae}. Le texte pourrait être trop court ou invalide.")
        return None
    except Exception as e:
        print(f"Erreur lors de la génération de l'audio avec gTTS : {e}")
        return None
# ------------------------------------------------------


if __name__ == '__main__':
    print("--- Test des Utilitaires ---")
    # ... (autres tests) ...

    print("\n--- Test de la Génération Audio (gTTS vers BytesIO) ---")
    sample_feedback_text_bytes = "Ceci est un test avec BytesIO. La qualité devrait être bonne."
    
    audio_bytes_io = generate_audio_feedback_gtts_bytes(sample_feedback_text_bytes)

    if audio_bytes_io:
        print(f"Objet BytesIO audio généré avec succès. Taille: {audio_bytes_io.getbuffer().nbytes} bytes.")
        print("Dans Streamlit, vous passeriez cet objet à st.audio().")
        # Pour le sauvegarder localement pour test (optionnel) :
        # with open("test_audio_from_bytesio.mp3", "wb") as f:
        #     f.write(audio_bytes_io.read())
        # print("Sauvegardé localement comme test_audio_from_bytesio.mp3 pour vérification.")
    else:
        print("Échec de la génération de l'objet BytesIO audio.")