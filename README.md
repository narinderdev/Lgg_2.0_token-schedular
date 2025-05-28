🚀 GHL OAuth Token Manager (FastAPI)
This project is a Python-based OAuth 2.0 integration using FastAPI for authenticating with GoHighLevel (GHL). It handles:

OAuth 2.0 authorization flow

Securely fetching access + refresh tokens

Storing refresh token

Refreshing the access token every 23 hours

Exposing useful endpoints (/, /auth, /auth/callback, /token)

1. Clone and install dependencies
git clone <your-repo-url>
cd LGG\ 2.0
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

2. Fill in .env file
Create a .env file at the root with the following:
GHL_CLIENT_ID=your_client_id
GHL_CLIENT_SECRET=your_client_secret
GHL_TOKEN_URL=https://services.leadconnectorhq.com/oauth/token
GHL_REDIRECT_URI=https://your-ngrok-id.ngrok-free.app/auth/callback
⚠️ Leave GHL_REFRESH_TOKEN empty for now. It will be populated after first auth.

3.🧑‍💻 Running the Application
uvicorn main:app --reload

4.Then start an ngrok tunnel:
ngrok http 8000
Copy the HTTPS URL and update it in your **.env** and **LeadConnector App Settings** as the redirect URI.

3.Begin OAuth Flow

Visit: https://<ngrok-url>/auth or (http://127.0.0.1:8000/auth)

Click Proceed after selecting your location

Redirects to /auth/callback with the code param

Success

Refresh token is stored to .env

Scheduler starts automatically:
✅ Access token refreshed!
🔁 Scheduler started for refreshing token every 23 hours.
Get Current Access Token

GET /token
🔁 Automatic Token Refresh
A background job runs every 23 hours

Refreshes the access token using the stored GHL_REFRESH_TOKEN

Updates .env if a new refresh token is issued
