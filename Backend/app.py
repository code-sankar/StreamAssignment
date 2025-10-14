from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps
import json
from config import Config
from models import OverlayManager

app = Flask(__name__)
app.config.from_object(Config)

# CORS setup
CORS(app, origins=["http://localhost:3000"])

# MongoDB setup with error handling
try:
    mongo = PyMongo(app)
    # Test connection
    mongo.db.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    print("Please check your MongoDB Atlas connection string in .env file")
    mongo = None

if mongo:
    overlay_manager = OverlayManager(mongo)
else:
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
    return json_response({'message': 'Livestream API is running!', 'database': 'connected'})

# Routes for Overlays CRUD
@app.route('/api/overlays', methods=['GET'])
def get_overlays():
    db_error = check_db_connection()
    if db_error:
        return db_error
        
    try:
        overlays = overlay_manager.get_all_overlays()
        # Convert ObjectId to string for JSON serialization
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

# Health check endpoint with DB status
@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = 'connected' if mongo and mongo.db.command('ping') else 'disconnected'
    return json_response({
        'status': 'healthy', 
        'message': 'Server is running',
        'database': db_status
    })

# Database connection test endpoint
@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        if mongo:
            # Try to ping the database
            mongo.db.command('ping')
            # Try to access the overlays collection
            overlays_count = mongo.db.overlays.count_documents({})
            return json_response({
                'status': 'success',
                'message': 'Database connection successful',
                'overlays_count': overlays_count,
                'database': 'livestream_app'
            })
        else:
            return json_response({'status': 'error', 'message': 'Database not connected'}, 500)
    except Exception as e:
        return json_response({'status': 'error', 'message': str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)