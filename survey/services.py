import os
import json
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    """Initializes Firebase app if not already initialized."""
    if not firebase_admin._apps:
        # Load credentials from individual ENV variables.
        try:
            cred_dict = {
                "type": os.environ.get('FIREBASE_TYPE'),
                "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
                "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                "auth_uri": os.environ.get('FIREBASE_AUTH_URI'),
                "token_uri": os.environ.get('FIREBASE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.environ.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.environ.get('FIREBASE_UNIVERSE_DOMAIN')
            }
            
            # Filter out None values to see if we missed any critical ones easily or leave validation to Certificate
            # But explicitly checking for some might be good.
            # However, `credentials.Certificate` validation is robust enough usually if we just pass the dict.
            # The previous logic had manual validation; we can rely on firebase_admin or keep it simple.
            
            # Important: Check if at least some key ones are present to avoid obscure errors
            if not cred_dict['project_id'] or not cred_dict['private_key'] or not cred_dict['client_email']:
                 raise ValueError("Missing critical Firebase environment variables (PROJECT_ID, PRIVATE_KEY, or CLIENT_EMAIL).")

            cred = credentials.Certificate(cred_dict)
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get('FIREBASE_DB_URL')
            })
            print("Firebase initialized successfully.")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase: {e}")

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
