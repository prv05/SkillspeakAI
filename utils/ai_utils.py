import subprocess
import requests
import whisper
import os
import json


def _groq_api_url():
    return os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')


def _groq_api_key():
    return os.getenv('GROQ_API_KEY', '').strip()


def _groq_default_model():
    return os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')


def _groq_fallback_models():
    env_models = os.getenv('GROQ_FALLBACK_MODELS', '').strip()
    if env_models:
        return [m.strip() for m in env_models.split(',') if m.strip()]
    return [
        'llama-3.1-8b-instant',
        'llama-3.1-70b-versatile',
        'mixtral-8x7b-32768'
    ]


def _resolve_model(model):
    # Backward compatibility for old local-model names.
    aliases = {
        'llama3': 'llama-3.3-70b-versatile',
        'mistral': 'mixtral-8x7b-32768',
        'default': _groq_default_model(),
        'advanced': 'llama-3.3-70b-versatile',
        'experimental': 'llama-3.3-70b-versatile'
    }
    if not model:
        return _groq_default_model()
    return aliases.get(model, model)

# Whisper transcription
def transcribe_audio(file_path):
    model = whisper.load_model('base')
    result = model.transcribe(file_path)
    return result['text']

def _groq_chat(prompt, model=None):
    api_key = _groq_api_key()
    if not api_key:
        raise ValueError('GROQ_API_KEY is not set in environment variables.')

    payload = {
        'model': _resolve_model(model),
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(_groq_api_url(), json=payload, headers=headers, timeout=45)
    response.raise_for_status()
    data = response.json()
    choices = data.get('choices', [])
    if choices:
        message = choices[0].get('message', {})
        return message.get('content', '').strip()
    return ''


def ollama_chat(prompt):
    # Backward-compatible wrapper name; now routed to Groq.
    return _groq_chat(prompt)

def get_ai_response(prompt, model=None):
    attempted_models = []
    primary_model = _resolve_model(model)
    fallback_models = [m for m in _groq_fallback_models() if m != primary_model]
    models_to_try = [primary_model] + fallback_models

    last_http_error = None
    for candidate_model in models_to_try:
        attempted_models.append(candidate_model)
        try:
            response = _groq_chat(prompt, model=candidate_model)
            if response:
                return response
        except requests.exceptions.HTTPError as e:
            details = ''
            if getattr(e, 'response', None) is not None:
                try:
                    error_data = e.response.json()
                    details = error_data.get('error', {}).get('message', '')
                except Exception:
                    details = e.response.text

            # Retry on model-level issues, otherwise return immediately.
            retryable_markers = [
                'blocked at the project level',
                'model',
                'not found',
                'unsupported'
            ]
            lowered = (details or '').lower()
            if any(marker in lowered for marker in retryable_markers):
                last_http_error = details or str(e)
                continue
            return f"AI HTTP error: {details or str(e)}"
        except requests.exceptions.RequestException as e:
            return f"AI network error: {str(e)}"
        except Exception as e:
            return f"AI error: {str(e)}"

    if last_http_error:
        return f"AI HTTP error: {last_http_error}. Tried models: {', '.join(attempted_models)}"
    return f"AI provider returned an empty response. Tried models: {', '.join(attempted_models)}"

def get_ai_feedback(user_input, model=None):
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