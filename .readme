== Livestream Video Player with Overlay ==

A full-stack web application for streaming live video with customizable overlays. Built with React, Flask, and MongoDB.

🚀 Features
🎥 Live Streaming
RTSP Stream Support: Play live streams from RTSP URLs

Browser-Compatible Video: Automatic RTSP to HLS conversion for browser playback

Video Controls: Play, pause, volume control, and fullscreen support

Responsive Player: Adapts to different screen sizes

🎨 Overlay Management
Custom Overlays: Add text and image overlays to your livestream

Real-time Positioning: Drag and position overlays anywhere on the video

Size Control: Resize overlays with pixel-perfect precision

Live Preview: See overlay changes in real-time

CRUD Operations: Create, read, update, and delete overlay configurations

💾 Data Persistence
MongoDB Integration: Cloud database for storing overlay configurations

RESTful API: Complete CRUD API for overlay management

Persistent Settings: Save and reload overlay positions and settings

🛠 Tech Stack
Frontend
React 18 - Modern UI framework

Tailwind CSS - Utility-first CSS framework

Axios - HTTP client for API calls

Video.js - Professional video player

Lucide React - Beautiful icons

Backend
Python Flask - Lightweight web framework

Flask-PyMongo - MongoDB integration

Flask-CORS - Cross-origin resource sharing

Gunicorn - Production WSGI server

Database & Deployment
MongoDB Atlas - Cloud database service

Render - Backend hosting platform

Vercel - Frontend hosting platform

📦 Installation & Setup
Prerequisites
Node.js (v16 or higher)

Python (v3.9 or higher)

MongoDB Atlas account

Backend Setup
Clone the repository

bash
git clone https://github.com/code-sankar/StreamAssignment.git
cd streamstudio/backend
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Environment Configuration
Create .env file:

env
MONGO_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/livestream_app?retryWrites=true&w=majority
SECRET_KEY=your-secret-key-here
Run the backend

bash
python app.py
Backend will run on http://localhost:

Frontend Setup
Navigate to frontend directory

bash
cd ../frontend
Install dependencies

bash
npm install
Environment Configuration
Create .env file:

env
REACT_APP_API_URL=http://localhost:/api
Start development server

bash
npm start
Frontend will run on http://localhost:3000

🚀 Deployment
Backend Deployment (Render)
Push code to GitHub

Connect repository to Render

Set environment variables in Render dashboard:

MONGO_URI: Your MongoDB Atlas connection string

SECRET_KEY: Secure random string

PYTHON_VERSION: 3.9.18

Build Command:

bash
pip install -r requirements.txt
Start Command:

bash
gunicorn --bind 0.0.0.0:$PORT wsgi:app
Frontend Deployment (Vercel)
Push code to GitHub

Connect repository to Vercel

Set environment variables:

REACT_APP_API_URL: Your Render backend URL (e.g., https://your-app.onrender.com/api)

Vercel will automatically deploy

📚 API Documentation
Base URL
text
https://your-backend.onrender.com/api
Endpoints
Health Check
http
GET /health
Response:

json
{
  "status": "healthy",
  "message": "Server is running",
  "database": "connected",
  "environment": "production"
}
Overlay Management
Get All Overlays

http
GET /overlays
Create Overlay

http
POST /overlays
Body:

json
{
  "name": "Welcome Text",
  "type": "text",
  "content": "Live Stream",
  "position": {
    "x": 50,
    "y": 10
  },
  "size": {
    "width": 200,
    "height": 50
  }
}
Update Overlay

http
PUT /overlays/:id
Delete Overlay

http
DELETE /overlays/:id
Get Single Overlay

http
GET /overlays/:id
Overlay Object Schema
typescript
interface Overlay {
  _id: string;
  name: string;
  type: 'text' | 'image';
  content: string;
  position: {
    x: number;  // Percentage (0-100)
    y: number;  // Percentage (0-100)
  };
  size: {
    width: number;   // Pixels
    height: number;  // Pixels
  };
  created_at: string;
  updated_at: string;
}
🎯 Usage Guide
Adding a Live Stream
Enter RTSP URL: In the stream controller, paste your RTSP stream URL

Start Stream: Click "Start Stream" to begin playback

Control Playback: Use video player controls to play, pause, or adjust volume

Managing Overlays
Create Overlay: Click "New Overlay" in the Overlay Manager

Choose Type: Select between text or image overlay

Configure Settings:

Name: Descriptive name for the overlay

Content: Text content or image URL

Position: Set X and Y coordinates (0-100%)

Size: Set width and height in pixels

Position Overlays:

Use the position sliders to move overlays

Adjust size for perfect fit

Toggle visibility with the eye icon

Real-time Updates: Changes appear instantly on the video stream

Example RTSP URLs for Testing
rtsp://your-test-stream-url/live

rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4

🗂 Project Structure
text
streamstudio/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # MongoDB models and OverlayManager
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── wsgi.py               # WSGI entry point
│   └── runtime.txt           # Python version specification
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoPlayer.js    # Video player component
│   │   │   └── OverlayManager.js # Overlay management UI
│   │   ├── App.js             # Main application component
│   │   ├── App.css            # Global styles
│   │   └── index.js           # React entry point
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── postcss.config.js
└── README.md
🔧 Configuration
MongoDB Setup
Create MongoDB Atlas Cluster

Sign up at MongoDB Atlas

Create a free M0 cluster

Configure network access (allow all IPs: 0.0.0.0/0)

Create database user with read/write permissions

Get Connection String

Format: mongodb+srv://username:password@cluster.xxxxx.mongodb.net/database?retryWrites=true&w=majority

Environment Variables
Backend (.env)

env
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
Frontend (.env)

env
REACT_APP_API_URL=your_backend_api_url
🐛 Troubleshooting
Common Issues
CORS Errors

Ensure backend CORS configuration includes your frontend domain

Check that environment variables are set correctly

MongoDB Connection Issues

Verify MongoDB Atlas network access settings

Check connection string format and credentials

Ensure database user has correct permissions

Video Playback Issues

RTSP streams require conversion to HLS for browser compatibility

Test with provided sample HLS streams first

Deployment Issues

Check Render/Vercel logs for error messages

Verify all environment variables are set

Ensure package versions are compatible

Debug Endpoints
The API provides debug endpoints to help troubleshoot:

GET /api/health - Check server and database status

GET /api/debug - View environment configuration

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Video.js for the robust video player

Tailwind CSS for the utility-first CSS framework

Render and Vercel for hosting services

MongoDB Atlas for cloud database services
