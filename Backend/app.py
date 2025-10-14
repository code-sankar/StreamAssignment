import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps
from urllib.parse import quote_plus
import json

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DPEe0TxhxCtrJ2ET0othTM7waFDuOP5y5S4ByHh6Poxm578YES21FC')
app.config['DEBUG'] = False

# CORS setup
CORS(app, origins=[
    "http://localhost:3000",
    "https://stream-assignment-seven.vercel.app",
    "http://localhost:5173",
    
])

mongo = None
overlay_manager = None

try:
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    
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
        'environment': 'production' if os.getenv('RENDER') else 'development'
    })

@app.route('/api/overlays', methods=['GET'])
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

@app.route('/api/overlays', methods=['POST'])
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

@app.route('/api/overlays/<overlay_id>', methods=['GET'])
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

@app.route('/api/overlays/<overlay_id>', methods=['PUT'])
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

@app.route('/api/overlays/<overlay_id>', methods=['DELETE'])
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

@app.route('/api/health', methods=['GET'])
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

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check environment and connection"""
    mongo_uri = os.getenv('MONGO_URI')
    
    return json_response({
        'render': bool(os.getenv('RENDER')),
        'mongo_uri_set': bool(mongo_uri),
        'mongo_uri_preview': mongo_uri.split('@')[0] + '...' if mongo_uri else 'not set',
        'python_version': sys.version,
        'environment_variables': list(os.environ.keys())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)