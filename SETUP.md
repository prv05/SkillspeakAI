# SkillSpeak AI - Setup and Run Guide

## Prerequisites

1. **Python 3.8+** installed
2. **MongoDB** installed and running locally
3. **Groq API key** available (for AI features)

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** On Windows, if PyAudio installation fails, use:
```bash
pip install pipwin
pipwin install pyaudio
```

## Step 2: Setup MongoDB

Make sure MongoDB is running on your system:

**Windows:**
```bash
# Start MongoDB service (usually starts automatically)
net start MongoDB

# Or check if it's running
mongosh "mongodb://localhost:27017"
```

**Linux/Mac:**
```bash
# Start MongoDB
sudo systemctl start mongod

# Check status
sudo systemctl status mongod
```

The database will be created automatically at: `mongodb://localhost:27017/skillspeak_ai`

## Step 3: Configure Groq API

1. Generate an API key from your Groq account.

2. Set the API key as an environment variable:
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your_groq_api_key_here"
   ```

3. Optional model override:
   ```bash
   # Windows PowerShell
   $env:GROQ_MODEL="llama-3.3-70b-versatile"
   ```

## Step 4: Run the Flask Backend

```bash
python app.py
```

The backend will start on: **http://127.0.0.1:5000**

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

## Step 5: Access the Application

### Backend API
- Root endpoint: http://127.0.0.1:5000/
- API endpoints: http://127.0.0.1:5000/api/*

### Frontend HTML Files
Open these files in your browser (using a local server like Live Server):
- `index.html` - Main page
- `login.html` - Login page
- `signup.html` - Sign up page
- `dashboard.html` - User dashboard
- `admin.html` - Admin panel
- `profile.html` - User profile
- `feedback.html` - Feedback page

**Recommended:** Use VS Code Live Server extension or Python's HTTP server:
```bash
# Python 3
python -m http.server 5500

# Then open: http://localhost:5500/index.html
```

## API Endpoints

- `/` - Root endpoint (health check)
- `/api/auth/*` - Authentication routes
- `/api/voice/*` - Voice interview routes
- `/api/feedback/*` - Feedback routes
- `/api/profile/*` - User profile routes
- `/api/dashboard/*` - Dashboard routes
- `/api/admin/*` - Admin routes
- `/api/session/*` - Session management routes

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongosh "mongodb://localhost:27017"`
- Check if port 27017 is available
- Verify MongoDB service is started

### Groq Connection Error
- Ensure `GROQ_API_KEY` is set in your shell before running the backend
- Verify internet access to `https://api.groq.com`
- Confirm `GROQ_MODEL` value is a supported model

### PyAudio Installation Issues (Windows)
```bash
pip install pipwin
pipwin install pyaudio
```

### Module Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Port Already in Use
- Change port in `app.py` line 81: `app.run(debug=True, port=5001)`
- Or stop the process using port 5000

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MongoDB (if not running automatically)
net start MongoDB

# 3. Set Groq API key
set GROQ_API_KEY=your_groq_api_key_here

# 4. Run the Flask backend
python app.py
```

## Environment Variables (Optional)

You can set these environment variables if needed:

- `MONGO_URI` - MongoDB connection string (default: `mongodb://localhost:27017/skillspeak_ai`)
- `JWT_SECRET` - JWT secret key (default: `supersecretjwtkey`)
- `UPLOAD_FOLDER` - Folder for uploads (default: `uploads/`)
- `GROQ_API_KEY` - Required Groq API key
- `GROQ_MODEL` - Optional model override (default: `llama-3.3-70b-versatile`)
- `GROQ_API_URL` - Optional endpoint override (default: `https://api.groq.com/openai/v1/chat/completions`)

