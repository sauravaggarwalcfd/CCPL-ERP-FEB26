"""One-time script to generate OAuth2 token for Google Sheets access.
Run this once: python generate_token.py
It will open a browser for consent and save token.json.
"""
import json
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_PATH = r"D:/CCPL ERP FEB26/client_secret_812520010098-nhsm408ui647ausblpam44tlpe5cpio2.apps.googleusercontent.com.json"
TOKEN_PATH = os.path.join(os.path.dirname(CREDENTIALS_PATH), 'token.json')

def main():
    from google_auth_oauthlib.flow import InstalledAppFlow

    print(f"Reading credentials from: {CREDENTIALS_PATH}")

    with open(CREDENTIALS_PATH, 'r') as f:
        cred_data = json.load(f)

    # Convert 'web' to 'installed' for InstalledAppFlow
    if 'web' in cred_data:
        client_config = {'installed': cred_data['web']}
    else:
        client_config = cred_data

    print("Opening browser for Google consent...")
    print("Please sign in and allow access to Google Sheets.")

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8085)

    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())

    print(f"\nToken saved to: {TOKEN_PATH}")
    print("You can now start the backend with: python -m uvicorn app.main:app --reload")

if __name__ == '__main__':
    main()
