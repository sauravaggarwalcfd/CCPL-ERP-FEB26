"""One-time script to generate OAuth2 token for Google Sheets access.

STEP 1: python generate_token.py --get-url
         -> Prints the Google auth URL. Open it in your browser, allow access.
         -> After allowing, browser redirects to localhost (shows error - that's OK).
         -> Copy the 'code=...' value from the URL bar.

STEP 2: python generate_token.py --code=PASTE_CODE_HERE
         -> Saves token.json. Done!
"""
import json
import os
import sys

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')


def get_flow():
    from google_auth_oauthlib.flow import InstalledAppFlow
    with open(CREDENTIALS_PATH, 'r') as f:
        cred_data = json.load(f)
    if 'web' in cred_data:
        client_config = {'installed': cred_data['web']}
    else:
        client_config = cred_data
    return InstalledAppFlow.from_client_config(
        client_config, SCOPES,
        redirect_uri='http://localhost'
    )


def step1_get_url():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    print("\n" + "="*60)
    print("STEP 1: Open this URL in your browser:")
    print("="*60)
    print(auth_url)
    print("="*60)
    print("\nAfter you click Allow, the browser will try to open")
    print("http://localhost?code=XXXX  (it will show an error - that's OK)")
    print("\nCopy the full URL from the address bar and run:")
    print('  python generate_token.py --code=PASTE_THE_CODE_HERE')
    print("\nThe code= is the long string after 'code=' in the URL.\n")


def step2_save_token(code):
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    with open(TOKEN_PATH, 'w') as f:
        f.write(creds.to_json())
    print(f"\ntoken.json saved to: {TOKEN_PATH}")
    print("Google Sheets is now connected!")
    print("Start the backend: python -m uvicorn app.main:app --reload")


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or '--get-url' in args:
        step1_get_url()
    elif any(a.startswith('--code=') for a in args):
        code = next(a.split('=', 1)[1] for a in args if a.startswith('--code='))
        step2_save_token(code)
    else:
        print("Usage:")
        print("  python generate_token.py --get-url")
        print("  python generate_token.py --code=YOUR_AUTH_CODE")
