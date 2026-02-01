import subprocess
import requests
import whisper
import os
import json
from requests.auth import HTTPBasicAuth

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_USER = "prv"
OLLAMA_PASS = "pratham05"

# Whisper transcription
def transcribe_audio(file_path):
    model = whisper.load_model('base')
    result = model.transcribe(file_path)
    return result['text']

# Ollama chat (Mistral-7B)
def ollama_chat(prompt):
    response = requests.post(f'{OLLAMA_URL}/api/generate', json={
        'model': OLLAMA_MODEL,
        'prompt': prompt
    })
    if response.status_code == 200:
        return response.json().get('response', '')
    return '' 

def get_ai_response(prompt, model="llama3"):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(
        OLLAMA_URL,
        json=payload,
        auth=HTTPBasicAuth(OLLAMA_USER, OLLAMA_PASS)
    )
    response.raise_for_status()
    data = response.json()
    if "message" in data:
        return data["message"]["content"]
    elif "messages" in data and data["messages"]:
        return data["messages"][-1]["content"]
    return "Sorry, I couldn't get a response from the AI."

def get_ai_feedback(user_input, model="llama3"):
    """Generate AI feedback for user input/suggestions"""
    prompt = f"""
    Analyze the following user input and provide structured feedback in JSON format:
    
    User Input: {user_input}
    
    Please provide feedback in this exact JSON format:
    {{
        "summary": "Brief summary of the input",
        "score": 8.5,
        "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
        "category": "general|technical|ui_ux|feature_request|bug_report"
    }}
    
    Score should be 1-10, suggestions should be actionable, and category should be one of the listed options.
    """
    
    try:
        ai_response = get_ai_response(prompt, model)
        return ai_response
    except Exception as e:
        # Fallback response if AI fails
        return json.dumps({
            "summary": f"User provided feedback: {user_input[:100]}...",
            "score": 7.0,
            "suggestions": [
                "Thank you for your feedback",
                "We will review this suggestion",
                "Please continue providing valuable input"
            ],
            "category": "general"
        }) 