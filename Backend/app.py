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

# Allowed Frontend Origins
allowed_origins = [
    "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
    "hhttp://localhost:5173/"
]
import os
import sys
import time
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

# Allowed Frontend Origins
allowed_origins = [
    "https://stream-assignment-mtxz1vrt9-sankars-projects-3d0835cc.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

#  CORS Setup 
CORS(
    app,
    origins=allowed_origins,
    supports_credentials=False,   
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)


# MongoDB Connection

mongo = None
overlay_manager = None

# Try to initialize MongoDB with retries and clearer fallbacks
mongo_uri = os.getenv(
    'MONGO_URI',
    'mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
)

if not mongo_uri:
    print("❌ MONGO_URI is not set. Please set the MONGO_URI environment variable.")
else:
    max_attempts = 3
    attempt = 0
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        try:
            print(f"Attempting to connect to MongoDB (attempt {attempt})...")
            app.config['MONGO_URI'] = mongo_uri
            # Do not create a persistent connection on import, let driver manage it
            app.config['MONGO_CONNECT'] = False
            mongo = PyMongo(app)
            # quick ping to ensure connectivity
            mongo.db.command('ping')
            print("✅ Successfully connected to MongoDB Atlas!")
            # Only import and init OverlayManager after successful DB connection
            from models import OverlayManager
            overlay_manager = OverlayManager(mongo)
            print("✅ OverlayManager initialized successfully!")
            last_error = None
            break
        except Exception as e:
            last_error = e
            print(f"❌ MongoDB connection attempt {attempt} failed: {e}")
            # short backoff before retry
            time.sleep(2 * attempt)

    if last_error and not mongo:
        print("❌ All MongoDB connection attempts failed. The app will continue to run, but database functionality will be disabled.")
        print(f"Last error: {last_error}")
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
        return json_response({'error': 'Database connection failed'}, 500)
    try:
        mongo.db.command('ping')
        return None
    except Exception as e:
        return json_response({'error': f'Database ping failed: {str(e)}'}, 500)

# Routes

@app.route('/')
def home():
    return json_response({
        'message': 'Livestream API is running!',
        'database': 'connected' if mongo else 'disconnected',
        'environment': 'production' if os.getenv('RENDER') else 'development',
        'cors': 'enabled'
    })

@app.route('/overlays', methods=['GET', 'POST', 'OPTIONS'])
def overlays():
    db_error = check_db_connection()
    if db_error:
        return db_error

    if request.method == 'GET':
        try:
            overlays = overlay_manager.get_all_overlays()
            for overlay in overlays:
                overlay['_id'] = str(overlay['_id'])
            return json_response(overlays)
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
            overlay['_id'] = str(overlay['_id'])
            return json_response(overlay, 201)
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
                'status': 'unavailable',
                'database': 'disconnected',
                'environment': 'production' if os.getenv('RENDER') else 'development'
            }, 503)
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': str(e),
            'database': 'disconnected'
        }, 500)

@app.route('/debug', methods=['GET', 'OPTIONS'])
def debug_info():
    mongo_uri_preview = None
    if os.getenv('MONGO_URI'):
        try:
            mongo_uri_preview = os.getenv('MONGO_URI').split('@')[0] + '...'
        except Exception:
            mongo_uri_preview = 'set (hidden)'
    origin = request.headers.get('Origin', 'Not provided')
    return json_response({
        'render': bool(os.getenv('RENDER')),
        'mongo_uri_set': bool(os.getenv('MONGO_URI')),
        'mongo_uri_preview': mongo_uri_preview or 'not set',
        'python_version': sys.version,
        'request_origin': origin,
        'cors_enabled': True,
        'db_connected': bool(mongo)
    })

# Extra safety: Always return CORS headers

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    # normalize origin to compare without trailing slash
    normalized = origin.rstrip('/') if origin else origin
    if normalized in [o.rstrip('/') for o in allowed_origins]:
        response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response

# Run the App
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

#  CORS Setup 
CORS(
    app,
    origins=allowed_origins,
    supports_credentials=False,   
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)


# MongoDB Connection

mongo = None
overlay_manager = None

try:
    mongo_uri = os.getenv(
        'MONGO_URI',
        'mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
    )
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")
    
    print(f"Attempting to connect to MongoDB...")
    app.config['MONGO_URI'] = mongo_uri
    app.config['MONGO_CONNECT'] = False
    mongo = PyMongo(app)
    
    # Test connection
    mongo.db.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")

    from models import OverlayManager
    overlay_manager = OverlayManager(mongo)
    print("✅ OverlayManager initialized successfully!")

except Exception as e:
    print(f"❌ MongoDB initialization failed: {str(e)}")
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
        return json_response({'error': 'Database connection failed'}, 500)
    try:
        mongo.db.command('ping')
        return None
    except Exception as e:
        return json_response({'error': f'Database ping failed: {str(e)}'}, 500)

# Routes

@app.route('/')
def home():
    return json_response({
        'message': 'Livestream API is running!',
        'database': 'connected' if mongo else 'disconnected',
        'environment': 'production' if os.getenv('RENDER') else 'development',
        'cors': 'enabled'
    })

@app.route('/overlays', methods=['GET', 'POST', 'OPTIONS'])
def overlays():
    db_error = check_db_connection()
    if db_error:
        return db_error

    if request.method == 'GET':
        try:
            overlays = overlay_manager.get_all_overlays()
            for overlay in overlays:
                overlay['_id'] = str(overlay['_id'])
            return json_response(overlays)
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
            overlay['_id'] = str(overlay['_id'])
            return json_response(overlay, 201)
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
        mongo.db.command('ping')
        return json_response({
            'status': 'healthy',
            'database': 'connected',
            'environment': 'production' if os.getenv('RENDER') else 'development'
        })
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': str(e),
            'database': 'disconnected'
        }, 500)

@app.route('/debug', methods=['GET', 'OPTIONS'])
def debug_info():
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

# Extra safety: Always return CORS headers

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response

# Run the App
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
