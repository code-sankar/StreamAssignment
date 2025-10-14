import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
except ImportError:
    # Fallback configuration if import fails
    class Config:
        MONGO_URI = os.getenv('MONGO_URI','mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        SECRET_KEY = os.getenv('SECRET_KEY', 'DPEe0TxhxCtrJ2ET0othTM7waFDuOP5y5S4ByHh6Poxm578YES21FC')
        DEBUG = False

app = Flask(__name__)
app.config.from_object(Config)

# CORS setup
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-frontend-app.onrender.com",
    "http://localhost:5000"
])

# MongoDB setup with enhanced error handling
try:
    mongo = PyMongo(app)
    mongo.db.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    mongo = None

# Import models after mongo is initialized
try:
    from models import OverlayManager
    if mongo:
        overlay_manager = OverlayManager(mongo)
    else:
        overlay_manager = None
except ImportError as e:
    print(f"❌ Models import error: {e}")
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
    return None

@app.route('/')
def home():
    db_error = check_db_connection()
    if db_error:
        return db_error
    return json_response({
        'message': 'Livestream API is running!', 
        'database': 'connected',
        'environment': 'production' if os.getenv('RENDER') else 'development'
    })

# Your existing routes here (GET, POST, PUT, DELETE for /api/overlays)
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
        db_status = 'connected' if mongo and mongo.db.command('ping') else 'disconnected'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)