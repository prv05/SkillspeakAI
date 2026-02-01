from flask import Blueprint, request, jsonify, g
from utils.ai_utils import get_ai_response
from models.chat import save_message, get_chat_history
from models.session import get_sessions_by_user
from utils.jwt_utils import token_required
import re
import ollama

voice_bp = Blueprint('voice', __name__)

# Helper functions for interview
def get_welcome_prompt():
    return "Welcome to the AI Interviewer. Please tell me your job role."

def ask_question(role):
    prompt = f"Generate one clear interview question for a candidate applying for a {role} role. Only return the question."
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    question = response['message']['content'].strip().replace('\n', ' ')
    return question

def evaluate_answer(question, answer):
    prompt = (
        f"Evaluate the following answer to an interview question on a scale of 1 to 10. "
        f"Also provide brief constructive feedback.\n\n"
        f"Question: {question}\nAnswer: {answer}\n\n"
        f"Respond in this format: Score: X/10\nFeedback: <your feedback>"
    )
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response['message']['content'].strip()
    score_match = re.search(r'Score:\s*(\d+)/10', content)
    feedback_match = re.search(r'Feedback:\s*(.*)', content)
    score = int(score_match.group(1)) if score_match else 0
    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback found."
    return score, feedback

def final_feedback(scores):
    avg = sum(scores) / len(scores) if scores else 0
    if avg >= 8:
        return f"Excellent performance! Your average score is {avg:.1f}/10. Keep it up!"
    elif avg >= 6:
        return f"Good job. Your average score is {avg:.1f}/10. Some improvement is possible."
    else:
        return f"Your average score is {avg:.1f}/10. Focus on practicing your communication and domain knowledge."

@voice_bp.route('/chat/send', methods=['POST'])
def send_message():
    data = request.json
    print('Received chat data:', data)  # Debug print
    user_id = data.get('user_id')
    role = data.get('role')
    message = data.get('message')
    session_id = data.get('session_id')
    chat_id = data.get('chat_id')
    if not user_id or not role or not message:
        print('Missing required fields:', data)
        return jsonify({'error': 'user_id, role, and message required'}), 400
    save_message(
        user_id=user_id,
        role=role,
        message=message,
        session_id=session_id,
        chat_id=chat_id
    )
    # Get AI response from Ollama
    ai_response = get_ai_response(message)
    save_message(
        user_id=user_id,
        role='ai',
        message=ai_response,
        session_id=session_id,
        chat_id=chat_id
    )
    print('Saved user and AI messages for user_id:', user_id)
    return jsonify({'message': ai_response}), 201

@voice_bp.route('/chat/history/<user_id>', methods=['GET'])
def chat_history(user_id):
    session_id = request.args.get('session_id')
    chat_id = request.args.get('chat_id')
    history = get_chat_history(user_id, session_id, chat_id)
    return jsonify([h for h in history]), 200

@voice_bp.route('/sessions', methods=['GET'])
@token_required
def get_user_sessions():
    sessions = get_sessions_by_user(g.user_id)
    # Format sessions for frontend
    formatted_sessions = []
    for session in sessions:
        # Handle different timestamp field names and formats
        timestamp = None
        if 'timestamp' in session:
            timestamp = session['timestamp']
        elif 'created_at' in session:
            timestamp = session['created_at']
        elif 'date' in session:
            timestamp = session['date']
        else:
            timestamp = datetime.utcnow()  # Default to current time
        
        # Format the timestamp
        if hasattr(timestamp, 'strftime'):
            formatted_date = timestamp.strftime('%Y-%m-%d %H:%M')
        else:
            formatted_date = str(timestamp)
        
        formatted_sessions.append({
            'type': 'Voice Chat',
            'date': formatted_date,
            'score': 'N/A',
            'duration': 'N/A',
            'focus': 'Communication'
        })
    return jsonify({'sessions': formatted_sessions}), 200

@voice_bp.route('/interview', methods=['POST'])
def run_voice_interview():
    """Run the AI voice interview session and return all results as JSON. Supports test mode with text answers."""
    # Check for test mode
    test_mode = False
    answers_override = []
    if request.is_json:
        data = request.get_json()
        test_mode = data.get('test', False)
        answers_override = data.get('answers', [])
    elif request.args.get('test') == 'true':
        test_mode = True
    results = {
        'questions': [],
        'answers': [],
        'scores': [],
        'feedbacks': [],
        'summary': ''
    }
    import speech_recognition as sr
    import pyttsx3
    import time
    import ollama
    import re
    recognizer = sr.Recognizer()
    def speak(text):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    def listen(idx=None):
        if test_mode:
            # Use predefined answers for testing
            if idx is not None and idx < len(answers_override):
                return answers_override[idx]
            return f"Test answer {idx+1 if idx is not None else ''}"
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except Exception:
                return ""
    def ask_question_local(role):
        pass  # Use module-level function
    def evaluate_answer_local(question, answer):
        pass  # Use module-level function
    def final_feedback_local(scores):
        pass  # Use module-level function
    
    # Start interview
    speak("Welcome to the AI Interviewer. Please tell me your job role.")
    role = listen(0) if test_mode else listen()
    if not role:
        speak("I didn't catch your role. Exiting.")
        return jsonify({'error': 'No role provided'}), 400
    scores = []
    for i in range(3):
        speak(f"Here comes question {i + 1}.")
        question = ask_question(role)
        speak(question)
        time.sleep(1 if test_mode else 7)
        speak("Please answer now.")
        answer = listen(i+1) if test_mode else listen()
        results['questions'].append(question)
        results['answers'].append(answer)
        if not answer:
            speak("Sorry, no answer detected. Moving on.")
            results['scores'].append(0)
            results['feedbacks'].append("No answer detected.")
            continue
        score, feedback = evaluate_answer(question, answer)
        scores.append(score)
        results['scores'].append(score)
        results['feedbacks'].append(feedback)
        speak(f"You scored {score} out of 10.")
        speak("Feedback: " + feedback)
    overall = final_feedback(scores)
    results['summary'] = overall
    speak("Interview complete.")
    speak(overall)
    return jsonify(results), 200

@voice_bp.route('/interview/step', methods=['POST'])
def interview_step():
    """Stepwise AI interview: returns the next prompt/question or feedback based on current state."""
    data = request.get_json()
    role = data.get('role', '').strip()
    answers = data.get('answers', [])
    step = len(answers)
    # Step 0: Welcome and ask for role
    if step == 0:
        prompt = get_welcome_prompt()
        return jsonify({'prompt': prompt, 'type': 'role'}), 200
    # Step 1: First question
    if step == 1:
        question = ask_question(role)
        return jsonify({'prompt': question, 'type': 'question', 'index': 1}), 200
    # Step 2-4: Next questions
    if 2 <= step <= 3:
        question = ask_question(role)
        return jsonify({'prompt': question, 'type': 'question', 'index': step}), 200
    # After 3 answers, evaluate all
    if step == 4:
        feedbacks = []
        scores = []
        for i, answer in enumerate(answers[1:]):
            question = ask_question(role)
            score, feedback = evaluate_answer(question, answer)
            feedbacks.append(feedback)
            scores.append(score)
        summary = final_feedback(scores)
        return jsonify({'type': 'feedback', 'feedbacks': feedbacks, 'scores': scores, 'summary': summary}), 200
    return jsonify({'prompt': 'Interview complete.'}), 200 