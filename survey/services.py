import os
import json
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    """Initializes Firebase app if not already initialized."""
    if not firebase_admin._apps:
        # Load credentials from ENV.
        firebase_creds_input = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_creds_input:
            try:
                # 1. Strategy: Check if it's a file path
                if os.path.isfile(firebase_creds_input):
                    # Load directly from file path
                    cred = credentials.Certificate(firebase_creds_input)
                    print(f"Loaded Firebase credentials from file: {firebase_creds_input}")
                else:
                    # 2. Strategy: Parse as JSON string
                    if isinstance(firebase_creds_input, str):
                        cred_dict = json.loads(firebase_creds_input)
                    else:
                        cred_dict = firebase_creds_input
                    
                    # Validation for dict mode
                    required_keys = ['type', 'project_id', 'private_key', 'client_email', 'token_uri']
                    missing_keys = [key for key in required_keys if key not in cred_dict]
                    
                    if missing_keys:
                        raise ValueError(f"FIREBASE_CREDENTIALS JSON is missing required keys: {', '.join(missing_keys)}")
                    
                    cred = credentials.Certificate(cred_dict)

                firebase_admin.initialize_app(cred, {
                    'databaseURL': os.environ.get('FIREBASE_DB_URL')
                })
                print("Firebase initialized successfully.")
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in FIREBASE_CREDENTIALS and not a valid file path: {e}")
            except Exception as e:
                # Re-raise if it's already one of our ValueErrors, otherwise wrap
                if isinstance(e, ValueError):
                    raise e
                raise Exception(f"Failed to initialize Firebase: {e}")
        else:
             raise ValueError("FIREBASE_CREDENTIALS environment variable not found. Please check your .env file.")

def save_entry(mode, location, questions):
    """
    Saves the entry to Firebase Realtime Database.
    Structure: /<mode>/<incremental_id>/...
    """
    initialize_firebase()
    
    # Reference to the specific mode node (e.g., /normal)
    ref = db.reference(f'/{mode}')
    
    # Logic to find the next incremental ID
    # We fetch the last key to determine the next number.
    # Note: In high currency, this needs transactions, but for this scale it's fine.
    snapshot = ref.order_by_key().limit_to_last(1).get()
    
    next_id = 1
    if snapshot:
        # Snapshot is a dict like {'5': {...}}, we take the key
        last_key = list(snapshot.keys())[0]
        try:
            next_id = int(last_key) + 1
        except ValueError:
            next_id = 1 # Fallback if keys aren't integers
            
    # Construct the data object exactly as requested
    new_entry = {
        'location': location,
        'questions': questions
    }
    
    # Save to /<mode>/<next_id>
    ref.child(str(next_id)).set(new_entry)
    
    return next_id
