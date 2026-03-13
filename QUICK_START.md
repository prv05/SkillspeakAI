# Quick Start Guide - SkillSpeak AI

## 🚀 Fastest Way to Run

### Option 1: Using the Batch Script (Windows)
```bash
run.bat
```

### Option 2: Manual Steps

#### 1. Install Dependencies (First time only)
```bash
pip install -r requirements.txt
```

#### 2. Start MongoDB
```bash
# Windows
net start MongoDB

# Or verify it's running
mongosh "mongodb://localhost:27017"
```

#### 3. Configure Groq API (for AI features)
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Optional: choose Groq model
$env:GROQ_MODEL="llama-3.3-70b-versatile"
```

#### 4. Run the Backend
```bash
python app.py
```

## ✅ Verify Everything is Running

1. **Backend API:** Open http://127.0.0.1:5000
   - Should show: `{"message": "SkillSpeak AI API is running!"}`

2. **Frontend:** Open any HTML file (e.g., `index.html`) using Live Server or:
   ```bash
   python -m http.server 5500
   ```
   Then open: http://localhost:5500/index.html

## 📋 Required Services

- ✅ **MongoDB** - Database (default: localhost:27017)
- ✅ **Groq API** - Cloud LLM provider (set GROQ_API_KEY)
- ✅ **Flask Backend** - API Server (default: localhost:5000)

## 🔧 Troubleshooting

**MongoDB not running?**
```bash
net start MongoDB
```

**Groq API key missing?**
```bash
set GROQ_API_KEY=your_groq_api_key_here
```

**Port 5000 in use?**
Edit `app.py` line 81: `app.run(debug=True, port=5001)`

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

**PyAudio install failed (Windows)?**
```bash
pip install pipwin
pipwin install pyaudio
```

## 📝 Full Documentation

See `SETUP.md` for detailed setup instructions.

