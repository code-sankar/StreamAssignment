import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    try:
        # Get MongoDB connection string
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://sankarjyotichetia57_db_user:U1IFPLMwvQcZfKE0@cluster0.cpddo24.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        database_name = os.getenv('DATABASE_NAME', 'DPEe0TxhxCtrJ2ET0othTM7waFDuOP5y5S4ByHh6Poxm578YES21FC')
        
        if not mongodb_uri:
            print(" MONGODB_URI not found in .env file")
            return False
        
        print(f"Connecting to MongoDB...")
        print(f"Database: {database_name}")
        
        # Connect to MongoDB
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Get database
        db = client[database_name]
        
        # Create collections
        collections = ['users', 'videos', 'comments', 'likes']
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection already exists: {collection_name}")
        
        # Create indexes for better performance
        db.videos.create_index([("title", "text"), ("description", "text")])
        db.videos.create_index("upload_date")
        db.comments.create_index("video_id")
        db.likes.create_index([("video_id", 1), ("user_id", 1)])
        
        print("Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("Please check your MongoDB Atlas connection string in .env file")
        return False

if __name__ == "__main__":
    setup_database()