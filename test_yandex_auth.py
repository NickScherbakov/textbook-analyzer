#!/usr/bin/env python3
"""
Script to test Yandex Cloud authentication and token generation.
This script helps verify that your OAuth token is working correctly
and can generate valid IAM tokens for API access.
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_iam_token(oauth_token):
    """
    Get IAM token using OAuth token
    
    Args:
        oauth_token: Yandex OAuth token
        
    Returns:
        dict: Response containing IAM token and other details
    """
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    response = requests.post(
        url,
        json={'yandexPassportOauthToken': oauth_token}
    )
    
    return response

def test_vision_api(folder_id, iam_token):
    """
    Test connection to Yandex Vision API
    
    Args:
        folder_id: Yandex Cloud folder ID
        iam_token: IAM token for authentication
        
    Returns:
        dict: Response from API
    """
    url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    
    # We're just going to check if we can connect, not actually send an image
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {iam_token}'
    }
    
    # Minimal payload to test authentication
    body = {
        'folderId': folder_id,
        'analyzeSpecs': []
    }
    
    response = requests.post(url, headers=headers, json=body)
    return response

def main():
    parser = argparse.ArgumentParser(description='Test Yandex Cloud authentication')
    parser.add_argument('--oauth', help='Yandex OAuth token (if not in env var)')
    parser.add_argument('--folder', help='Yandex Cloud folder ID (if not in env var)')
    args = parser.parse_args()
    
    # Get OAuth token from args or environment
    oauth_token = args.oauth or os.environ.get('YANDEX_OAUTH_TOKEN')
    if not oauth_token:
        print("Error: YANDEX_OAUTH_TOKEN not set in environment or passed as argument")
        sys.exit(1)
    
    print("=== Testing Yandex Cloud Authentication ===\n")
    print("1. Getting IAM token from OAuth token...")
    response = get_iam_token(oauth_token)
    
    if response.status_code != 200:
        print(f"✘ Failed to get IAM token: {response.status_code} - {response.text}")
        sys.exit(1)
    
    token_data = response.json()
    iam_token = token_data.get('iamToken')
    expires_at = token_data.get('expiresAt', 'Unknown')
    
    print(f"✓ Success! IAM token received.")
    print(f"  Expires at: {expires_at}")
    print(f"  IAM token: {iam_token[:15]}...{iam_token[-4:]} (truncated for security)")
    
    # Try to test vision API
    folder_id = args.folder or os.environ.get('YANDEX_FOLDER_ID')
    if folder_id:
        print("\n2. Testing Yandex Vision API access...")
        api_response = test_vision_api(folder_id, iam_token)
        
        if api_response.status_code == 200 or api_response.status_code == 400:
            # 400 is actually OK here - it means authentication worked but our empty payload isn't valid
            print(f"✓ API connection successful! Response code: {api_response.status_code}")
            if api_response.status_code == 400:
                print("  (HTTP 400 is expected with our test payload - it means auth is working)")
        else:
            print(f"✘ API connection failed: {api_response.status_code} - {api_response.text}")
    else:
        print("\n2. Skipping Vision API test - YANDEX_FOLDER_ID not set")
    
    print("\n=== Authentication Test Complete ===")
    
    # If everything worked, print the environment setup instructions
    if response.status_code == 200:
        print("\nTo use this token in your application, set these environment variables:")
        print(f"export YANDEX_IAM_TOKEN='{iam_token}'")
        if folder_id:
            print(f"export YANDEX_FOLDER_ID='{folder_id}'")
    
if __name__ == "__main__":
    main()