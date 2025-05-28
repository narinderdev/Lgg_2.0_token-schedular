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

3. Start FastAPI app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

4. Start ngrok
In a separate terminal:

ngrok http 8000
Copy the HTTPS forwarding URL and update .env:
GHL_REDIRECT_URI=https://your-ngrok-id.ngrok-free.app/auth/callback

5. Configure Redirect URI in GHL
Go to your GHL Developer Dashboard and add the same redirect URI:
https://your-ngrok-id.ngrok-free.app/auth/callback
✅ OAuth Flow
Go to /
→ http://localhost:8000/
→ Returns: "GHL Token Manager is running. Go to /auth to begin."

Visit /auth(http://127.0.0.1:8000/auth
)
→ Redirects to GHL’s location selection

Remember:
You are not logged in to marketplace

After clicking Proceed
→ GHL redirects to /auth/callback?code=...

main.py handles the code
→ Sends POST to GHL to exchange for access + refresh token
→ Saves refresh token to .env
→ Scheduler starts for auto-refresh

⏱️ Scheduled Job
Once the initial token is received, the app automatically starts a job using APScheduler that:

Runs every 23 hours

Refreshes the access token using the saved refresh token

You'll see logs like:

✅ Access token refreshed!
🔁 Scheduler started for refreshing token every 23 hours.
🔗 API Endpoints
Method	Endpoint	Description
GET	/	Health check message(http://127.0.0.1:8000)
GET	/auth	Begins OAuth login flow(http://127.0.0.1:8000/auth
)
GET	/auth/callback	Handles GHL redirect & token save()
GET	/token	Returns current access token
