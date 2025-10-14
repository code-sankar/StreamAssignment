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

# Enhanced CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
            "stream-assignment-seven.vercel.app",
            "stream-assignment-git-main-sankars-projects-3d0835cc.vercel.app",
            "https://stream-assignment-git-*.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Add CORS headers manually for additional security
@app.after_request
def after_request(response):
    # Get the origin from the request
    origin = request.headers.get('Origin', '')
    
    # List of allowed origins
    allowed_origins = [
        "http://localhost:3000",
        "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app/",
        "https://stream-assignment-*.vercel.app",
        "https://*.vercel.app"
    ]
    
    # Check if the origin is in our allowed list or matches a pattern
    if any(origin == allowed or ( '*' in allowed and origin.endswith(allowed.split('*')[1])) for allowed in allowed_origins):
        response.headers.add('Access-Control-Allow-Origin', origin)
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    
    return response

# Handle OPTIONS requests for CORS preflight
@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        return response

# Initialize MongoDB with proper error handling
mongo = None
overlay_manager = None

try:
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")
    
    print(f"Attempting to connect to MongoDB...")
    print(f"MongoDB URI: {mongo_uri.split('@')[0]}...")  # Log without password
    
    # Configure MongoDB connection
    app.config['MONGO_URI'] = mongo_uri
    app.config['MONGO_CONNECT'] = False  # Lazy connection
    
    mongo = PyMongo(app)
    
    # Test the connection
    mongo.db.command('ping')
    print("Successfully connected to MongoDB Atlas!")
    
    # Import and initialize OverlayManager after successful connection
    from models import OverlayManager
    overlay_manager = OverlayManager(mongo)
    print("OverlayManager initialized successfully!")
    
except Exception as e:
    print(f"MongoDB initialization failed: {str(e)}")
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

# Your existing routes with proper CORS handling
@app.route('/api/overlays', methods=['GET', 'OPTIONS'])
def get_overlays():
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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
            'environment': 'production' if os.getenv('RENDER') else 'development',
            'cors': 'enabled'
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
    if request.method == 'OPTIONS':
        return json_response({'status': 'preflight'})
    
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