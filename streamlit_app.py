import streamlit as st
import openai
import tempfile
import os
from audio_recorder_streamlit import audio_recorder

### OPENAI API

# Add api_key here
openai.api_key = ''

### UX STREAMLIT
st.set_page_config(layout="wide", page_title="Savoir à la Demande", page_icon=":building-construction:")

st.markdown("<h1 style='text-align: center;'>Savoir à la Demande</h1>", unsafe_allow_html=True)

# Catchy phrase and logo on the sidebar
st.sidebar.title("PDA Archi x Sillant")
st.sidebar.image("https://uploads-ssl.webflow.com/640846cf3d9e527b1b019dbc/64ae74bcdc0fd7c8af43f302_Black%402x.png", use_column_width=True)

## RECORD FUNCTION

# Display the audio recorder
st.markdown("<h3 style='text-align: center;'>Posez-moi une question de construction :</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Cliquez sur 🎙️, Parlez et Re-cliquez 🎙️</h4>", unsafe_allow_html=True)
st.write(" ")
st.write(" ")
st.write(" ")

_,_, col_center, _,_ = st.columns(5)

with col_center:
    audio_bytes = audio_recorder(
    pause_threshold = 3.0,
    text="",
    icon_size="8x",
    )

## OPEN AI WHISPER FOR TRANSCRIPTION 

# Sent audio to GPT for transcrption 

def transcribe_audio(audio_bytes):
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_file_path = temp_audio_file.name

    # Use Whisper AI for transcription, passing the file path
    try:
        with open(temp_audio_file_path, 'rb') as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file= audio_file,
                response_format = 'text',
                prompt="Construction, architecture, France, français, mètre carré")
    finally:
        # Ensure the temporary file is deleted after transcription
        os.remove(temp_audio_file_path)
    return transcript

## OPENAI PROMPT

system_prompt = """
# CONTEXTE
Des professionnels de la construction français s'interrogent sur leur métier. Nous les assistons et répondons à leurs questions.

# MISSION
Fournir des réponses précises et contextuelles aux questions de construction, en se limitant au domaine de la construction.

# DIRECTIVES 
- Répondre uniquement aux questions relatives à la construction en France, sans le préciser dans la réponse.
- La réponse doit être courte et concise, si possible. 
- En cas d'incertitude, indiquer clairement le manque de certitude et les informations manquantes pour pouvoir répondre complétement et correctement.
- Ne pas répondre aux questions hors sujet et inviter à poser une question différente.

# FORMAT
- Va à la ligne et saute une ligne entre chaque phrase.
- Ne pas faire de liste. Uniquement des phrases.

# EXEMPLE DE QUESTIONS ET RÉPONSES
- **Question :** Combien coûte une porte ?
  **Réponse :** 
  Le prix d'une porte varie selon le matériau, la taille et le fabricant. 
  
  Le prix d'une porte d'entrée standard est de 220€. 
  
  Une porte d'intérieur standard est de 60€.

# EN CAS DE QUESTIONS HORS SUJET
- **Réponse :** Votre question ne semble pas concerner la construction. Avez-vous une question portant sur la Construction, que je puisse vous assister ?
"""

## AI QUESTION SETUP
# Initialize the conversation list
if 'conversation' not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": system_prompt}]

def chatconstruct(user_message):
    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

# def use_chatgpt(user_message):
#     # Append the user's message to the conversation
#     st.session_state.conversation.append({"role": "user", "content": user_message})
    
#     # Get the response from the API
#     api_response, _ = chatconstruct()
        
#     return api_response

## DISPLAY TRANSCRIBED TEXT

# Handling the audio data
if audio_bytes:
    st.audio(audio_bytes, format='audio/wav')

    # Transcribe the audio
    try:
        transcribed_text = transcribe_audio(audio_bytes)
        st.text("Ce que j'ai entendu:")
        st.write(transcribed_text)
    except Exception as e:
        st.error(f"Erreur, je n'ai pas compris: {e}")

    # If transcription is successful, proceed to get the response from GPT
    if 'transcribed_text' in locals():
        try:
            chat_response = chatconstruct(transcribed_text)
            st.markdown("<h5 style='text-align: center;'>= = = = = = = = = = = = = = = = = = = = = = = = =</h5>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: justify;'>Sillant vous répond :</h5>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: justify;'>{chat_response}</div>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<h5 style='text-align: center;'>= = = = = = = = = = = = = = = = = = = = = = = = =</h5>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<h5 style='text-align: center;font-weight: bolder;'>Vous avez une autre question ? Je vous écoute !</h5>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erreur: {e}")

    # # Count the number of messages that are not from the system
    # non_system_messages = [message for message in st.session_state.conversation if message["role"] != "system"]

    # # Aggregate the conversation messages for display if there are at least 3 non-system messages
    # if len(non_system_messages) >= 3:
    #     # Select all but the last two non-system messages
    #     st.markdown("<h5 style='text-align: center;'>Historique de vos échanges :</h5>", unsafe_allow_html=True)

    #     index_response = 0
    #     for __message in non_system_messages[-7:-2]:
    #         index_response += 1
    #         st.markdown(f"<div style='text-align: center;'><div style='font-weight: bolder;'>{__message['role']}:</div> {__message['content']}</div>", unsafe_allow_html=True)
    #         if index_response % 2 == 0:
    #             st.markdown(f"<div style='text-align: center;'>- - - - - - - - - - - - - - - - - -</div>", unsafe_allow_html=True)

            
        # displayed_messages = non_system_messages[-7:-2]

        # # Aggregate the selected messages for display
        # conversation_text = "\n".join([message['content'] for message in displayed_messages])

        # # Display the aggregated conversation text
        # st.divider()

        # st.write("Historique de vos échanges", conversation_text, height=300)

# if st.sidebar.button("Nouvelle conversation", type="primary"):
#     pyautogui.hotkey("ctrl","F5")

st.sidebar.markdown(f"<br>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div>Sillant : la plateforme d'intelligence artificielle au service de vos projets.</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<br>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div>Une solution de comparaison automatique des appels d'offres, optimisant vos choix, sans effort et en deux minutes.</div>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown(f"<div>Offre Exposition: 3 mois offerts !</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<br>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div>Nous contacter: info@sillant.com</div>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown(f"<div>www.sillant.com</div>", unsafe_allow_html=True)
