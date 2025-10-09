#!/usr/bin/env python3
"""Get your Fivetran Group ID"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv('backend/queen-ai/.env')

FIVETRAN_API_KEY = os.getenv('FIVETRAN_API_KEY')
FIVETRAN_API_SECRET = os.getenv('FIVETRAN_API_SECRET')

auth_string = f"{FIVETRAN_API_KEY}:{FIVETRAN_API_SECRET}"
auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')

HEADERS = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

print("Fetching your Fivetran groups...")
response = requests.get("https://api.fivetran.com/v1/groups", headers=HEADERS)

if response.status_code == 200:
    groups = response.json().get('data', {}).get('items', [])
    print(f"\nFound {len(groups)} group(s):\n")
    for group in groups:
        print(f"Group ID: {group['id']}")
        print(f"Name: {group['name']}")
        print(f"Created: {group['created_at']}")
        print("-" * 50)
    
    if groups:
        correct_id = groups[0]['id']
        print(f"\n✅ Update your .env with:")
        print(f"FIVETRAN_GROUP_ID={correct_id}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
