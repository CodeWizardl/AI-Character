# AI Character Assistant

## Overview

The **AI Character Assistant** is an interactive application built with Streamlit that simulates conversational AI personas with unique profiles and speaking styles. It leverages natural language processing and voice synthesis to create a rich, engaging user experience. Users can interact with the AI via text or voice, configure custom character profiles, and receive dynamic responses tailored to the character's personality and emotional state.

![WhatsApp Image 2025-01-09 at 18 12 04_33e959be](https://github.com/user-attachments/assets/e0a444fe-710a-4c99-945c-692c3c751b5c)

#### Chat with character as per you interest

![Screenshot 2025-01-09 181314](https://github.com/user-attachments/assets/ee711089-0d48-4092-95c6-02a724149a6a)


## Features

### Working Demo

#### Deployed Application or Local Setup
- The application can be run locally using Streamlit.
- Dependencies are managed via `requirements.txt`.
- Launch the app with `streamlit run app.py`.

#### Sample Conversations
- Casual chat: "Hey Luna, how's it going?"
  - Response: "Hey there! I'm doing great. What about you?"
- Professional query: "Luna, what do you know about AI advancements?"
  - Response: "Indeed, AI is progressing rapidly, especially in areas like NLP and robotics."

#### Character Background
- Characters have customizable profiles including:
  - **Name:** e.g., Luna
  - **Age:** e.g., 25
  - **Gender:** Male/Female/Non-binary
  - **Interests:** Technology, Arts, Science, etc.
  - **Personality Traits:** Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism

#### Feature Demonstration
1. **Voice Input and Output**:
   - Speak to the AI and receive responses in natural-sounding synthesized speech.
2. **Emotionally Adaptive Responses**:
   - The AI adjusts its tone and content based on the emotional sentiment of user input.
3. **Dynamic Personality Engine**:
   - The AI exhibits behavior consistent with its configured personality traits.
4. **Customizable Characters**:
   - Users can create characters with unique communication styles (casual/professional).

---

## Technical Documentation

### Architecture Overview
The application is structured into three main layers:
1. **Frontend**: User interface built using Streamlit.
2. **Middleware**: Character personality engine and memory management.
3. **Backend**: Integration with AI models and voice synthesis.

### System Components
1. **Streamlit UI**
   - Dynamic layout for character customization and chat interface.
   - Sidebar for voice settings and personality configuration.

2. **Personality Engine**
   - Determines character responses based on:
     - Personality traits
     - Emotional state
     - Communication style

3. **Voice Input and Output**
   - Speech recognition via `speech_recognition` library.
   - Text-to-speech synthesis using `pyttsx3` with gender-specific voices.

4. **Memory Management**
   - Short-term memory: Tracks the last 10 interactions.
   - Long-term memory: Stores historical interactions for deeper context.

5. **AI Model Integration**
   - Leverages Google Generative AI for natural language understanding and response generation.

### AI Model Integration
- **Model**: Google Gemini-1.5-pro
- **API**: `google.generativeai`
- **Key Features**:
  - Context-aware response generation
  - Persona-based interaction

### Data Flow Diagrams
#### User Interaction Flow
1. User inputs text/voice.
2. Input processed by the Personality Engine.
3. AI model generates a response.
4. Personality Engine adjusts emotional state and response style.
5. Response displayed and optionally synthesized into speech.

#### Backend Data Flow
1. User input -> Preprocessing -> AI model query.
2. AI response -> Postprocessing -> Personality adjustment.
3. Final response -> UI and memory storage.

### Future Expansion Possibilities
1. **Multilingual Support**
   - Expand voice recognition and synthesis to additional languages.
2. **Emotion Recognition**
   - Use facial recognition to detect user emotions for better response adaptation.
3. **Improved Memory System**
   - Introduce topic-based clustering for long-term memory.
4. **Custom Character Avatars**
   - Add visuals that adapt to emotional states and communication styles.
5. **Advanced Analytics**
   - Integrate usage statistics and feedback for continuous improvement.

---

## Installation and Setup

### Prerequisites
1. Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables for Google Generative AI API:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

### Running the Application
1. Clone the repository:
   ```bash
   git clone https://github.com/CodeWizardl/AI-Character.git
   ```
2. Navigate to the project directory:
   ```bash
   cd AI-Character
   ```
3. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

---

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

