# 🏋️ Exercise Form Analyzer

AI-powered exercise form analysis with user authentication and progress tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- At least 4GB RAM
- Webcam or video files for analysis

### Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5001
   ```

## 🎯 Features

### 🔐 User Authentication
- **Sign up/Login** with email and password
- **Google OAuth** integration (optional)
- **Persistent sessions** - stay logged in between app restarts
- **User profiles** and account management

### 🏋️ Exercise Analysis
- **5 Exercise Types**: Push-ups, Pull-ups, Squats, Planks, Tricep Dips
- **AI-Powered Analysis** using MediaPipe and LSTM models
- **Real-time Feedback** with accuracy scores
- **Mistake Detection** with specific improvement tips
- **Video Processing** with visual feedback overlay

### 📊 Progress Tracking
- **Exercise History** - track all your workouts
- **Accuracy Analytics** - see improvement over time
- **Progress Visualization** - charts and statistics
- **Video Storage** - access your analysis videos anytime

## 🎮 How to Use

1. **Create Account**: Sign up with email/password or Google
2. **Select Exercise**: Choose from 5 available exercise types
3. **Record Video**: Upload a video or use webcam
4. **Get Analysis**: AI analyzes your form and provides feedback
5. **Track Progress**: View your history and improvement over time

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # Authentication forms
├── auth_utils.py          # Authentication utilities
├── dataset_angles.py       # Angle calculation functions
├── pushup_lstm.py         # LSTM model for analysis
├── requirements.txt       # Python dependencies
├── run_app.bat           # Windows batch file to run app
├── .env                  # Environment variables
├── templates/            # HTML templates
├── static/              # CSS and JavaScript
├── models/              # AI model files
├── data/                # Demo videos
├── uploads/             # User uploaded videos
├── output/              # Analysis result videos
└── instance/            # Database files
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Google OAuth Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:5001/auth/google/callback`
6. Update `.env` file with your credentials

## 🗄️ Database

The application uses SQLite database with the following tables:
- **Users**: Account information and profiles
- **User Sessions**: Authentication and session management
- **Exercise History**: Analysis results and progress tracking

## 📊 Data Storage

All data is stored locally on your computer:
- **Database**: `instance/exercise_analyzer.db`
- **Videos**: `uploads/` and `output/` directories
- **Models**: `models/` directory

## 🛠️ Development

### Running in Development Mode
```bash
python app.py
```

### Database Management
The database is automatically created on first run. To reset:
```bash
# Delete the database file
rm instance/exercise_analyzer.db
# Restart the app to recreate
python app.py
```

## 🎯 Supported Exercises

1. **Push-ups** - Upper body strength and form
2. **Pull-ups** - Back and bicep development
3. **Squats** - Lower body strength and mobility
4. **Planks** - Core stability and endurance
5. **Tricep Dips** - Arm strength and definition

## 🔍 Technical Details

- **Backend**: Flask with SQLAlchemy
- **AI Models**: LSTM neural networks for form analysis
- **Computer Vision**: MediaPipe for pose detection
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Database**: SQLite for local storage
- **Authentication**: Flask-Login with session management

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `app.py` (line 730)
2. **Database errors**: Delete `instance/exercise_analyzer.db` and restart
3. **Session issues**: Clear browser cookies and try again
4. **Video processing errors**: Ensure video files are in supported formats (MP4, AVI, MOV)

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for models and videos

## 📱 Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔒 Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Secure session management
- Input validation and sanitization
- Local data storage (no cloud uploads)

## 🎉 Getting Started

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run the app**: `python app.py`
3. **Open browser**: Go to `http://localhost:5001`
4. **Create account**: Sign up with email or Google
5. **Start analyzing**: Choose an exercise and upload a video!

---

**Built with ❤️ for fitness enthusiasts who want to perfect their form!**