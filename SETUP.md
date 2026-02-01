# SkillSpeak AI - Setup and Run Guide

## Prerequisites

1. **Python 3.8+** installed
2. **MongoDB** installed and running locally
3. **Ollama** installed and running (for AI features)

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

## Step 3: Setup Ollama (AI Model Server)

1. **Install Ollama:**
   - Download from: https://ollama.ai
   - Follow installation instructions for your OS

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Pull required models:**
   ```bash
   ollama pull mistral
   ollama pull llama3
   ```

   The app uses `mistral` model by default, but `llama3` is also available.

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

### Ollama Connection Error
- Ensure Ollama is running: Check http://localhost:11434
- Verify models are pulled: `ollama list`
- Check if port 11434 is available

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

# 3. Start Ollama (in a separate terminal)
ollama serve

# 4. Pull AI models (in a separate terminal)
ollama pull mistral
ollama pull llama3

# 5. Run the Flask backend
python app.py
```

## Environment Variables (Optional)

You can set these environment variables if needed:

- `MONGO_URI` - MongoDB connection string (default: `mongodb://localhost:27017/skillspeak_ai`)
- `JWT_SECRET` - JWT secret key (default: `supersecretjwtkey`)
- `UPLOAD_FOLDER` - Folder for uploads (default: `uploads/`)
- `OLLAMA_URL` - Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Default AI model (default: `mistral`)

