from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

class OverlayManager:
    def __init__(self, mongo):
        self.mongo = mongo
        self.overlays = mongo.db.overlays
    
    def create_overlay(self, data):
        try:
            overlay = {
                'name': data['name'],
                'type': data['type'],
                'content': data['content'],
                'position': {
                    'x': int(data['position']['x']),
                    'y': int(data['position']['y'])
                },
                'size': {
                    'width': int(data['size']['width']),
                    'height': int(data['size']['height'])
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            result = self.overlays.insert_one(overlay)
            return self.get_overlay(str(result.inserted_id))
        except Exception as e:
            print(f"Error creating overlay: {e}")
            return None
    
    def get_all_overlays(self):
        try:
            return list(self.overlays.find().sort('created_at', -1))
        except Exception as e:
            print(f"Error getting overlays: {e}")
            return []
    
    def get_overlay(self, overlay_id):
        try:
            return self.overlays.find_one({'_id': ObjectId(overlay_id)})
        except (InvalidId, Exception) as e:
            print(f"Error getting overlay {overlay_id}: {e}")
            return None
    
    def update_overlay(self, overlay_id, data):
        try:
            update_data = {
                'name': data['name'],
                'type': data['type'],
                'content': data['content'],
                'position': {
                    'x': int(data['position']['x']),
                    'y': int(data['position']['y'])
                },
                'size': {
                    'width': int(data['size']['width']),
                    'height': int(data['size']['height'])
                },
                'updated_at': datetime.utcnow()
            }
            
            result = self.overlays.update_one(
                {'_id': ObjectId(overlay_id)},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                return self.get_overlay(overlay_id)
            return None
        except (InvalidId, Exception) as e:
            print(f"Error updating overlay {overlay_id}: {e}")
            return None
    
    def delete_overlay(self, overlay_id):
        try:
            result = self.overlays.delete_one({'_id': ObjectId(overlay_id)})
            return result.deleted_count > 0
        except (InvalidId, Exception) as e:
            print(f"Error deleting overlay {overlay_id}: {e}")
            return False