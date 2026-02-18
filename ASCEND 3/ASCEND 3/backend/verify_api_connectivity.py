import sys
import os
import json
import urllib.request
import urllib.error

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import app, db
from models import User

def verify_connectivity():
    with app.app_context():
        print("--- API Connectivity Verification ---")
        
        # 1. Get Mentor
        mentor = User.query.filter_by(role='mentor').first()
        if not mentor:
            print("ERROR: No mentor user found in database.")
            return

        print(f"Target Mentor: {mentor.username} (ID: {mentor.id})")

        # 2. Generate Token
        try:
            token = mentor.generate_auth_token()
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            print(f"Generated Token: {token[:15]}...")
        except Exception as e:
            print(f"ERROR generating token: {e}")
            return

        # 3. Request Headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # 4. Test endpoints
        endpoints = [
            'http://127.0.0.1:5000/api/mentor/dashboard',
            'http://127.0.0.1:5000/api/mentor/questions'
        ]

        for url in endpoints:
            print(f"\nTesting Endpoint: {url}")
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    status = response.getcode()
                    body = response.read().decode('utf-8')
                    print(f"SUCCESS (Status {status})")
                    print(f"Response Preview: {body[:100]}...")
            except urllib.error.HTTPError as e:
                print(f"FAILURE (HTTP {e.code}): {e.reason}")
                print(f"Error Body: {e.read().decode('utf-8')}")
            except urllib.error.URLError as e:
                print(f"FAILURE (Connection Error): {e.reason}")
                print("Make sure the Flask server is running on port 5000!")

if __name__ == "__main__":
    verify_connectivity()
