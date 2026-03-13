# 🎤 SkillSpeak AI

An AI-powered interview preparation and practice platform that helps users improve their communication skills through interactive voice-based mock interviews.

## 📌 Overview

SkillSpeak AI is a comprehensive interview training application that leverages artificial intelligence to conduct realistic mock interviews, provide real-time feedback, and track user progress. The platform combines speech recognition, natural language processing, and AI-driven evaluation to create an immersive learning experience.

## ✨ Features

- **🎯 AI-Powered Mock Interviews**: Practice with AI interviewer tailored to your job role
- **🗣️ Voice Recognition**: Real-time speech-to-text conversion for natural conversations
- **📊 Instant Feedback**: Get detailed scores and constructive feedback on your answers
- **📈 Progress Tracking**: Monitor your improvement with session history and analytics
- **👤 User Profiles**: Personalized dashboard with streak tracking and performance metrics
- **🔐 Secure Authentication**: JWT-based authentication system
- **👨‍💼 Admin Panel**: Comprehensive user management and analytics
- **💬 Chat Interface**: Text-based practice mode for flexibility
- **🎨 Modern UI**: Clean and intuitive user interface

## 🎥 Demo Video

Watch the full demo video to see SkillSpeak AI in action:

📹 **[Watch Demo Video on Google Drive](https://drive.google.com/file/d/1FZqjrOKiA44FxBaGDkaRsGVdJUwMaAb7/view?usp=drive_link)**



**Demo Highlights:**
- User registration and login
- Voice-based mock interview
- Real-time AI feedback
- Progress tracking dashboard
- Profile management

## 📸 Screenshots

### User Dashboard
![User Dashboard](./images/user%20dashboard.png)

### Interview Session - Part 1
![Interview Session 1](./images/interview%201.png)

### Interview Session - Part 2
![Interview Session 2](./images/interview%202.png)

### Live Feedback
![Live Feedback](./images/live%20feedback.png)

### Admin Dashboard
![Admin Dashboard](./images/admin%20dashboard.png)

### Feedback Section
![Feedback Section](./images/feedback%20section.png)

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **MongoDB** - NoSQL database
- **PyMongo** - MongoDB driver for Python
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing

### AI & Speech
- **Groq API** - LLM inference API (OpenAI-compatible endpoint)
- **SpeechRecognition** - Speech-to-text conversion
- **pyttsx3** - Text-to-speech engine
- **OpenAI Whisper** - Advanced speech recognition

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Responsive Design** - Mobile-friendly interface

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MongoDB (local or Atlas)
- Groq API key (for AI features)
- Microphone (for voice interviews)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/skillspeak-ai.git
cd skillspeak-ai
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If PyAudio installation fails on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### 3. Setup MongoDB

Make sure MongoDB is running:

**Windows:**
```bash
net start MongoDB
```

**Linux/Mac:**
```bash
sudo systemctl start mongod
```

The application will automatically create the database at: `mongodb://localhost:27017/skillspeak_ai`

### 4. Configure Groq API

1. Create/get your API key from Groq console.
2. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your_groq_api_key_here"

   # Optional model override
   $env:GROQ_MODEL="llama-3.3-70b-versatile"
   ```

### 5. Configuration

Update [config.py](config.py) with your settings:
```python
MONGO_URI = "mongodb://localhost:27017/skillspeak_ai"
JWT_SECRET_KEY = "your-secret-key-here"  # Change this!
```

## 🎮 Usage

### Running the Application

**Option 1: Quick Start (2 Terminals)**

Terminal 1 - Backend:
```bash
python app.py
```

Terminal 2 - Frontend:
```bash
python -m http.server 5500
```

Then open: [http://localhost:5500/index.html](http://localhost:5500/index.html)

**Option 2: Using VS Code Live Server**
1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### Accessing the Application

- **Homepage**: http://localhost:5500/index.html
- **Backend API**: http://127.0.0.1:5000
- **Login**: http://localhost:5500/login.html
- **Signup**: http://localhost:5500/signup.html
- **Dashboard**: http://localhost:5500/dashboard.html

## 📁 Project Structure

```
skillspeak-ai/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── mongo_client.py             # MongoDB connection
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── models/                     # Database models
│   ├── user.py                # User model
│   ├── chat.py                # Chat/message model
│   ├── session.py             # Interview session model
│   ├── feedback.py            # Feedback model
│   └── system_settings.py     # System settings
│
├── routes/                     # API routes
│   ├── auth.py                # Authentication endpoints
│   ├── voice.py               # Voice interview endpoints
│   ├── dashboard.py           # Dashboard endpoints
│   ├── profile.py             # Profile management
│   ├── admin.py               # Admin panel endpoints
│   ├── session.py             # Session management
│   └── feedback.py            # Feedback endpoints
│
├── utils/                      # Utility functions
│   ├── ai_utils.py            # AI/Groq integration
│   └── jwt_utils.py           # JWT authentication helpers
│
├── static/                     # Static assets (optional)
├── screenshots/                # Screenshots for README
│
└── Frontend Files:
    ├── index.html             # Landing page
    ├── login.html             # Login page
    ├── signup.html            # Registration page
    ├── dashboard.html         # User dashboard
    ├── chat.html              # Chat interface
    ├── admin.html             # Admin panel
    ├── profile.html           # User profile
    ├── feedback.html          # Feedback page
    ├── script.js              # Frontend JavaScript
    └── styles.css             # Global styles
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Interview
- `POST /api/voice/interview` - Start full voice interview
- `POST /api/voice/interview/step` - Step-by-step interview
- `POST /api/voice/chat/send` - Send chat message
- `GET /api/voice/chat/history/<user_id>` - Get chat history

### Dashboard
- `GET /api/dashboard/stats` - Get user statistics
- `GET /api/dashboard/sessions` - Get session history

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/<user_id>` - Update user
- `DELETE /api/admin/users/<user_id>` - Delete user

## 🧪 Testing

Run tests in test mode:
```bash
python test_speech_to_text.py
python test_user_management.py
python test_search_sort.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `net start MongoDB`
- Check connection string in [config.py](config.py)

### PyAudio Installation Fails
```bash
pip install pipwin
pipwin install pyaudio
```

### Groq API Not Responding
- Ensure `GROQ_API_KEY` is set in your environment
- Verify outbound HTTPS access to `https://api.groq.com`
- Optionally set `GROQ_MODEL` to a supported model name

### Microphone Not Working
- Check browser permissions for microphone access
- Ensure microphone is not being used by another application

## 🔒 Security

- Change the JWT secret key in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Regular security audits



## 👨‍💻 Author

**Your Name**
- GitHub: [@prv05](https://github.com/prv05)
- Email: prathamvernekar05@gmail.com

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast LLM inference
- [Flask](https://flask.palletsprojects.com/) community
- [MongoDB](https://www.mongodb.com/) documentation
- All contributors and users

## 📞 Support

For support, email prathamvernekar05@gmail.com or open an issue on GitHub.

---

⭐ **If you find this project helpful, please give it a star!** ⭐
