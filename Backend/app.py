import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DPEe0TxhxCtrJ2ET0othTM7waFDuOP5y5S4ByHh6Poxm578YES21FC')
app.config['DEBUG'] = False
app.url_map.strict_slashes = False

# Allowed Frontend Origins - FIXED: Removed invalid URL
allowed_origins = [
    "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

# CORS Setup - SIMPLIFIED
CORS(app, origins=allowed_origins)

# MongoDB Connection
mongo = None
overlay_manager = None

try:
    # Use the direct MongoDB URI without .env file issues
    mongo_uri = 'mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/livestream_app?retryWrites=true&w=majority&appName=Cluster0'
    
    print("Attempting to connect to MongoDB...")
    print(f"MongoDB URI: {mongo_uri.split('@')[0]}...")
    
    app.config['MONGO_URI'] = mongo_uri
    app.config['MONGO_CONNECT'] = False
    
    # Initialize PyMongo
    mongo = PyMongo(app)
    
    # Test connection with error handling
    print("Testing MongoDB connection...")
    mongo.db.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Import and initialize OverlayManager
    from models import OverlayManager
    overlay_manager = OverlayManager(mongo)
    print("✅ OverlayManager initialized successfully!")

except Exception as e:
    print(f"❌ MongoDB initialization failed: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    mongo = None
    overlay_manager = None

# Helper Functions
def json_response(data, status=200):
    return app.response_class(
        response=json.dumps(data, default=str),
        status=status,
        mimetype='application/json'
    )

def check_db_connection():
    if not mongo:
        return json_response({'error': 'Database connection not initialized'}, 500)
    try:
        mongo.db.command('ping')
        return None
    except Exception as e:
        return json_response({'error': f'Database ping failed: {str(e)}'}, 500)

# Routes
@app.route('/')
def home():
    db_status = 'connected' if mongo else 'disconnected'
    return json_response({
        'message': 'Livestream API is running!',
        'database': db_status,
        'environment': 'production' if os.getenv('RENDER') else 'development'
    })

@app.route('/overlays', methods=['GET', 'POST', 'OPTIONS'])
def overlays():
    db_error = check_db_connection()
    if db_error:
        return db_error

    if request.method == 'GET':
        try:
            overlays_list = overlay_manager.get_all_overlays()
            for overlay in overlays_list:
                overlay['_id'] = str(overlay['_id'])
            return json_response(overlays_list)
        except Exception as e:
            return json_response({'error': str(e)}, 500)

    elif request.method == 'POST':
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
            else:
                return json_response({'error': 'Failed to create overlay'}, 500)
                
        except Exception as e:
            return json_response({'error': str(e)}, 500)

@app.route('/overlays/<overlay_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def overlay_by_id(overlay_id):
    db_error = check_db_connection()
    if db_error:
        return db_error

    try:
        if request.method == 'GET':
            overlay = overlay_manager.get_overlay(overlay_id)
            if overlay:
                overlay['_id'] = str(overlay['_id'])
                return json_response(overlay)
            return json_response({'error': 'Overlay not found'}, 404)

        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return json_response({'error': 'No JSON data provided'}, 400)
            
            overlay = overlay_manager.update_overlay(overlay_id, data)
            if overlay:
                overlay['_id'] = str(overlay['_id'])
                return json_response(overlay)
            return json_response({'error': 'Overlay not found'}, 404)

        elif request.method == 'DELETE':
            success = overlay_manager.delete_overlay(overlay_id)
            if success:
                return json_response({'message': 'Overlay deleted successfully'})
            return json_response({'error': 'Overlay not found'}, 404)

    except Exception as e:
        return json_response({'error': str(e)}, 500)

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    try:
        if mongo:
            mongo.db.command('ping')
            return json_response({
                'status': 'healthy',
                'database': 'connected',
                'environment': 'production' if os.getenv('RENDER') else 'development'
            })
        else:
            return json_response({
                'status': 'error',
                'message': 'MongoDB not initialized',
                'database': 'disconnected'
            }, 500)
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': str(e),
            'database': 'disconnected'
        }, 500)

@app.route('/debug', methods=['GET', 'OPTIONS'])
def debug_info():
    mongo_status = 'connected' if mongo else 'disconnected'
    overlay_manager_status = 'initialized' if overlay_manager else 'failed'
    
    return json_response({
        'mongo_status': mongo_status,
        'overlay_manager_status': overlay_manager_status,
        'python_version': sys.version,
        'allowed_origins': allowed_origins
    })

# Test route to check MongoDB directly
@app.route('/test-mongo', methods=['GET'])
def test_mongo():
    try:
        if mongo:
            # Try to list collections
            collections = mongo.db.list_collection_names()
            # Try to count overlays
            overlays_count = mongo.db.overlays.count_documents({})
            
            return json_response({
                'status': 'success',
                'collections': collections,
                'overlays_count': overlays_count,
                'message': 'MongoDB is working correctly'
            })
        else:
            return json_response({
                'status': 'error',
                'message': 'MongoDB not initialized'
            }, 500)
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__
        }, 500)

# Run the App
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}...")
    print(f"Allowed origins: {allowed_origins}")
    app.run(host='0.0.0.0', port=port, debug=False)