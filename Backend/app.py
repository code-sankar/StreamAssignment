import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-123')
app.config['DEBUG'] = False

# Simple and effective CORS configuration
# Option 1: Allow specific origins
allowed_origins = [
    "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
    "https://stream-assignment-*.vercel.app"
]

# Option 2: For development, allow all origins (remove in production)
CORS(app, origins=allowed_origins)

# Or use this simpler approach that handles everything:
# CORS(app)  # This allows all origins - good for development

# Initialize MongoDB with proper error handling
mongo = None
overlay_manager = None

try:
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")
    
    print(f"Attempting to connect to MongoDB...")
    print(f"MongoDB URI: {mongo_uri.split('@')[0]}...")
    
    # Configure MongoDB connection
    app.config['MONGO_URI'] = mongo_uri
    app.config['MONGO_CONNECT'] = False
    
    mongo = PyMongo(app)
    
    # Test the connection
    mongo.db.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Import and initialize OverlayManager after successful connection
    from models import OverlayManager
    overlay_manager = OverlayManager(mongo)
    print("✅ OverlayManager initialized successfully!")
    
except Exception as e:
    print(f"❌ MongoDB initialization failed: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    mongo = None
    overlay_manager = None

def json_response(data, status=200):
    return app.response_class(
        response=json.dumps(data, default=str),
        status=status,
        mimetype='application/json'
    )

def check_db_connection():
    if not mongo:
        return json_response({'error': 'Database connection failed'}, 500)
    
    try:
        mongo.db.command('ping')
        return None
    except Exception as e:
        return json_response({'error': f'Database ping failed: {str(e)}'}, 500)

@app.route('/')
def home():
    return json_response({
        'message': 'Livestream API is running!', 
        'database': 'connected' if mongo else 'disconnected',
        'environment': 'production' if os.getenv('RENDER') else 'development',
        'cors': 'enabled'
    })

# API Routes
@app.route('/api/overlays', methods=['GET', 'OPTIONS'])
def get_overlays():
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        overlays = overlay_manager.get_all_overlays()
        for overlay in overlays:
            overlay['_id'] = str(overlay['_id'])
        return json_response(overlays)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/api/overlays', methods=['POST', 'OPTIONS'])
def create_overlay():
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        data = request.get_json()
        if not data:
            return json_response({'error': 'No JSON data provided'}, 400)
            
        required_fields = ['name', 'type', 'content', 'position', 'size']
        
        for field in required_fields:
            if field not in data:
                return json_response({'error': f'Missing field: {field}'}, 400)
        
        overlay = overlay_manager.create_overlay(data)
        if overlay:
            overlay['_id'] = str(overlay['_id'])
            return json_response(overlay, 201)
        return json_response({'error': 'Failed to create overlay'}, 500)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/api/overlays/<overlay_id>', methods=['GET', 'OPTIONS'])
def get_overlay(overlay_id):
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        overlay = overlay_manager.get_overlay(overlay_id)
        if overlay:
            overlay['_id'] = str(overlay['_id'])
            return json_response(overlay)
        return json_response({'error': 'Overlay not found'}, 404)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/api/overlays/<overlay_id>', methods=['PUT', 'OPTIONS'])
def update_overlay(overlay_id):
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        data = request.get_json()
        if not data:
            return json_response({'error': 'No JSON data provided'}, 400)
            
        overlay = overlay_manager.update_overlay(overlay_id, data)
        if overlay:
            overlay['_id'] = str(overlay['_id'])
            return json_response(overlay)
        return json_response({'error': 'Overlay not found'}, 404)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/api/overlays/<overlay_id>', methods=['DELETE', 'OPTIONS'])
def delete_overlay(overlay_id):
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        success = overlay_manager.delete_overlay(overlay_id)
        if success:
            return json_response({'message': 'Overlay deleted successfully'})
        return json_response({'error': 'Overlay not found'}, 404)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    try:
        if mongo:
            mongo.db.command('ping')
            db_status = 'connected'
        else:
            db_status = 'disconnected'
            
        return json_response({
            'status': 'healthy', 
            'message': 'Server is running',
            'database': db_status,
            'environment': 'production' if os.getenv('RENDER') else 'development'
        })
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': str(e),
            'database': 'disconnected'
        }, 500)

@app.route('/api/debug', methods=['GET', 'OPTIONS'])
def debug_info():
    """Debug endpoint to check environment and connection"""
    mongo_uri = os.getenv('MONGO_URI')
    origin = request.headers.get('Origin', 'Not provided')
    
    return json_response({
        'render': bool(os.getenv('RENDER')),
        'mongo_uri_set': bool(mongo_uri),
        'mongo_uri_preview': mongo_uri.split('@')[0] + '...' if mongo_uri else 'not set',
        'python_version': sys.version,
        'request_origin': origin,
        'cors_enabled': True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)