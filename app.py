import os
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Any
import streamlit as st
from PIL import Image
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
import pyperclip
from translate import Translator
import pyttsx3
import io
import base64
import speech_recognition as sr

def voice_to_text() -> str:
    """Convert voice input to text using speech recognition"""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Record audio from microphone
        with sr.Microphone() as source:
            st.info("Listening... (Speak now)")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            # Listen for audio input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            st.info("Processing speech...")
        
        # Convert speech to text
        text = recognizer.recognize_google(audio, language=st.session_state.get('voice_language', 'en'))
        return text
    
    except sr.WaitTimeoutError:
        st.warning("No speech detected within timeout period")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results; {str(e)}")
        return ""
    except sr.UnknownValueError:
        st.warning("Could not understand audio")
        return ""
    except Exception as e:
        st.error(f"Error processing voice input: {str(e)}")
        return ""

def text_to_speech(text: str, gender: str) -> str:
    """Convert text to speech with gender-specific voice using memory buffer"""
    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()
        
        # Configure voice based on gender
        voices = engine.getProperty('voices')
        if gender.lower() == "male":
            engine.setProperty('voice', voices[0].id)
        elif gender.lower() == "female":
            engine.setProperty('voice', voices[1].id)
        else:
            # For non-binary, use default voice with middle pitch
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('pitch', 150)
        
        # Get speech speed from session state or use default
        speed = st.session_state.get('voice_speed', 150)
        engine.setProperty('rate', speed)
        
        # Create a bytes buffer for the audio
        audio_buffer = io.BytesIO()
        
        def write_audio(audio):
            audio_buffer.write(audio)
        
        # Configure the engine to use our callback
        engine.connect('write', write_audio)
        
        # Generate the speech
        engine.say(text)
        engine.runAndWait()
        
        # Get the audio data
        audio_data = audio_buffer.getvalue()
        
        # Close the buffer
        audio_buffer.close()
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode()
        
        # Create audio HTML with autoplay
        audio_html = f'''
            <audio autoplay>
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            </audio>
        '''
        return audio_html
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return ""

@dataclass
class CharacterProfile:
    name: str
    age: int
    gender: str
    interests: List[str]
    background: str
    communication_style: str
    personality_traits: Dict[str, float]
    speaking_style: Dict[str, str]

@dataclass
class EmotionalState:
    valence: float
    arousal: float
    dominance: float

class PersonalityEngine:
    def __init__(self, profile: CharacterProfile):
        self.profile = profile
        self.traits = self.profile.personality_traits
        self.interests = self.profile.interests
        self.values = ["helpfulness", "knowledge", "creativity"]
        self.emotional_state = EmotionalState(0.5, 0.5, 0.5)
        
        self.speaking_styles = {
            "casual": {
                "greetings": ["Hey!", "Hi there!", "What's up?", "Hey, how's it going?"],
                "responses": ["Cool!", "Awesome!", "That's interesting!", "Got it!"],
                "closings": ["See ya!", "Later!", "Take care!", "Catch you later!"]
            },
            "professional": {
                "greetings": ["Hello", "Good day", "Greetings", "Welcome"],
                "responses": ["I understand", "Indeed", "Certainly", "That's correct"],
                "closings": ["Best regards", "Thank you", "Regards", "Have a good day"]
            }
        }
    
    def update_emotional_state(self, user_input: str) -> None:
        positive_words = {"happy", "good", "great", "awesome", "excellent", "thanks", "please"}
        negative_words = {"sad", "bad", "awful", "terrible", "angry", "upset"}
        
        words = user_input.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        valence_change = (positive_count - negative_count) * 0.1
        self.emotional_state.valence = max(0.0, min(1.0, 
            self.emotional_state.valence + valence_change * (1.0 - self.traits["neuroticism"])))
        
        arousal_change = (len(words) / 20.0) * self.traits["extraversion"]
        self.emotional_state.arousal = max(0.0, min(1.0,
            self.emotional_state.arousal + arousal_change - 0.1))
        
        dominance_modifier = self.traits["conscientiousness"] - self.traits["neuroticism"]
        self.emotional_state.dominance = max(0.0, min(1.0,
            self.emotional_state.dominance + dominance_modifier * 0.05))
    
    def get_response_style(self):
        style = self.profile.communication_style
        
        if self.emotional_state.valence < 0.3:
            return {
                "greeting": "I understand this might be difficult...",
                "response": random.choice(self.speaking_styles[style]["responses"]),
                "closing": "I'm here to help if you need anything."
            }
        else:
            return {
                "greeting": random.choice(self.speaking_styles[style]["greetings"]),
                "response": random.choice(self.speaking_styles[style]["responses"]),
                "closing": random.choice(self.speaking_styles[style]["closings"])
            }

class ConversationMemory:
    def __init__(self, max_memory: int = 10):
        self.short_term: List[Dict] = []
        self.long_term: List[Dict] = []
        self.max_memory = max_memory
    
    def add_memory(self, interaction: Dict[str, str]):
        self.short_term.append(interaction)
        if len(self.short_term) > self.max_memory:
            self.long_term.append(self.short_term.pop(0))
    
    def get_relevant_context(self, query: str) -> str:
        recent_context = [f"{m['role']}: {m['content']}" for m in self.short_term[-3:]]
        return "\n".join(recent_context)

class AICharacter:
    def __init__(self, profile: CharacterProfile):
        self.profile = profile
        self.personality = PersonalityEngine(profile)
        self.memory = ConversationMemory()
    
    def process_interaction(self, user_input: str) -> str:
        context = self.memory.get_relevant_context(user_input)
        self.personality.update_emotional_state(user_input)
        style = self.personality.get_response_style()
        
        prompt = f"""You are {self.profile.name}, a {self.profile.age}-year-old {self.profile.gender} AI assistant.
        Background: {self.profile.background}
        Communication Style: {self.profile.communication_style}
        Current Context: {context}
        
        Response Guidelines:
        - Use {self.profile.communication_style} communication style
        - Show personality consistent with a {self.profile.age}-year-old {self.profile.gender}
        - Express interests in: {', '.join(self.profile.interests)}
        - Maintain conversation flow using appropriate {self.profile.communication_style} language
        
        User Message: {user_input}
        
        Respond as {self.profile.name}, keeping in mind your personality and communication style.
        """
        return prompt

def handle_user_input(input_text: str, is_voice: bool = False):
    """Handle both voice and text input in a unified way"""
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)

    enhanced_prompt = st.session_state.ai_character.process_interaction(input_text)
    
    with st.chat_message("assistant"):
        response = st.session_state.chat_model.send_message(enhanced_prompt).text
        st.markdown(response)
        
        try:
            audio_html = text_to_speech(response, st.session_state.character_profile.gender)
            if audio_html:
                st.components.v1.html(audio_html, height=0)
        except Exception as e:
            st.error(f"Error with response speech: {str(e)}")
        
        st.session_state.ai_character.memory.add_memory({
            "role": "user",
            "content": input_text
        })
        st.session_state.ai_character.memory.add_memory({
            "role": "assistant",
            "content": response
        })
    
    st.session_state.messages.append({"role": "assistant", "content": response})

def configure_character():
    st.sidebar.header("Configure AI Character")
    
    name = st.sidebar.text_input("Character Name", value="Luna")
    age = st.sidebar.number_input("Age", min_value=18, max_value=80, value=25)
    gender = st.sidebar.radio("Gender", ["Female", "Male", "Non-binary"])

    communication_style = st.sidebar.radio(
        "Communication Style",
        ["casual", "professional"],
        format_func=lambda x: x.capitalize()
    )
    
    interests = st.sidebar.multiselect(
        "Interests",
        ["Technology", "Science", "Arts", "Philosophy", "Music", "Literature", "Sports"],
        default=["Technology", "Science"]
    )
    
    background = f"I am {name}, a {age}-year-old {gender.lower()} AI assistant with interests in {', '.join(interest.lower() for interest in interests)}. "
    background += "I enjoy helping people while maintaining a "
    background += "friendly and relaxed" if communication_style == "casual" else "professional and formal"
    background += " demeanor."
    
    personality_traits = {
        "openness": st.sidebar.slider("Openness", 0.0, 1.0, 0.7),
        "conscientiousness": st.sidebar.slider("Conscientiousness", 0.0, 1.0, 0.8),
        "extraversion": st.sidebar.slider("Extraversion", 0.0, 1.0, 0.6),
        "agreeableness": st.sidebar.slider("Agreeableness", 0.0, 1.0, 0.75),
        "neuroticism": st.sidebar.slider("Neuroticism", 0.0, 1.0, 0.3)
    }
    
    return CharacterProfile(
        name=name,
        age=age,
        gender=gender,
        interests=interests,
        background=background,
        communication_style=communication_style,
        personality_traits=personality_traits,
        speaking_style={}
    )

def main():
    st.set_page_config(page_title="AI Character Assistant", page_icon="🤖", layout="wide")
    load_dotenv()

    if "character_profile" not in st.session_state:
        st.session_state.character_profile = configure_character()
    else:
        st.session_state.character_profile = configure_character()

    if "ai_character" not in st.session_state or "character_profile" in st.session_state:
        st.session_state.ai_character = AICharacter(st.session_state.character_profile)
    
    if "model" not in st.session_state:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        st.session_state.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        st.session_state.chat_model = st.session_state.model.start_chat()
        
        st.session_state.chat_model.send_message(
            f"You are {st.session_state.character_profile.name}. {st.session_state.character_profile.background} "
            "Please maintain this persona throughout our conversation."
        )

    if 'voice_speed' not in st.session_state:
        st.session_state.voice_speed = 150

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
        f"""
        <h1 style="text-align: center;">Chat with {st.session_state.character_profile.name} 🤖</h1>
        """,
        unsafe_allow_html=True
        )
        
        if "messages" not in st.session_state:
            initial_greeting = f"{st.session_state.ai_character.personality.get_response_style()['greeting']} I'm {st.session_state.character_profile.name}. How can I help you today?"
            st.session_state.messages = [
                {"role": "assistant", "content": initial_greeting}
            ]
            try:
                audio_html = text_to_speech(initial_greeting, st.session_state.character_profile.gender)
                if audio_html:
                    st.components.v1.html(audio_html, height=0)
            except Exception as e:
                st.error(f"Error with initial greeting speech: {str(e)}")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input area with voice button
        input_col1, input_col2 = st.columns([6, 1])
        
        # Voice input button
        with input_col2:
            if st.button("🎤", help="Click to speak"):
                voice_input = voice_to_text()
                if voice_input:
                    handle_user_input(voice_input, is_voice=True)

        # Text input
        if prompt := st.chat_input("Your message..."):
            handle_user_input(prompt, is_voice=False)

    with col2:
        st.header("Character Profile")
        
        if st.session_state.character_profile.gender == "Female":
            st.image("girl_image.jpg", caption=f"This is {st.session_state.character_profile.name}", use_column_width=True)
        elif st.session_state.character_profile.gender == "Male":
            st.image("boy_image.jpeg", caption=f"This is {st.session_state.character_profile.name}", use_column_width=True)
            
        st.write(f"**Name:** {st.session_state.character_profile.name}")
        st.write(f"**Age:** {st.session_state.character_profile.age}")
        st.write(f"**Gender:** {st.session_state.character_profile.gender}")
        st.write(f"**Style:** {st.session_state.character_profile.communication_style.capitalize()}")
        
        st.subheader("Interests")
        for interest in st.session_state.character_profile.interests:
            st.write(f"- {interest}")
        
        st.subheader("Personality Traits")
        for trait, value in st.session_state.character_profile.personality_traits.items():
            st.progress(value, f"{trait.capitalize()}")

    # Voice settings in sidebar
    with st.sidebar:
        st.header("Voice Settings")
        voice_language = st.selectbox(
            "Voice Language",
            ["en", "es", "fr", "de", "it", "ja", "ko", "zh"],
            format_func=lambda x: {
                "en": "English",
                "es": "Spanish",
                "fr": "French", 
                "de": "German",
                "it": "Italian",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese"
            }[x]
        )
        
        new_speed = st.slider("Speech Speed", min_value=100, max_value=200, value=st.session_state.voice_speed, step=10)
        if new_speed != st.session_state.voice_speed:
            st.session_state.voice_speed = new_speed

if __name__ == "__main__":
    main()