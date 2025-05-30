from fastapi import FastAPI, Request
import os
import json
import requests
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from scheduler import start_scheduler
from token_manager import refresh_access_token, get_token
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
load_dotenv()
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    refresh_token = os.getenv("GHL_REFRESH_TOKEN")
    if refresh_token:
        try:
            await refresh_access_token()
            start_scheduler()
        except Exception as e:
            print("⚠️ Refresh failed during startup, waiting for /auth callback.")
            print("Reason:", e)
    else:
        print("🔁 No refresh token available yet. Complete auth at /auth")

# @app.get("/")
# def root():
#     return {"message": "GHL Token Manager is running. Go to /auth to begin."}
@app.get("/")
def root():
    return RedirectResponse(url="/auth")


@app.get("/auth")
def redirect_to_ghl():
    base_url = "https://marketplace.leadconnectorhq.com/oauth/chooselocation"
    client_id = os.getenv("GHL_CLIENT_ID")
    redirect_uri = os.getenv("GHL_REDIRECT_URI")
    scopes = "contacts.readonly calendars.readonly campaigns.readonly"

    redirect_url = (
        f"{base_url}?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
    )
    return RedirectResponse(url=redirect_url)

@app.get("/auth/callback")
def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h3>❌ Authorization code missing</h3>", status_code=400)

    payload = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("GHL_CLIENT_ID"),
        "client_secret": os.getenv("GHL_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.getenv("GHL_REDIRECT_URI")
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(os.getenv("GHL_TOKEN_URL"), data=payload, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        expires_in = tokens.get("expires_in", 86399)

        # Save refresh token to .env
        lines = []
        if os.path.exists(".env"):
            with open(".env", "r") as file:
                lines = file.readlines()

        with open(".env", "w") as file:
            replaced = False
            for line in lines:
                if line.startswith("GHL_REFRESH_TOKEN="):
                    file.write(f"GHL_REFRESH_TOKEN={refresh_token}\n")
                    replaced = True
                else:
                    file.write(line)
            if not replaced:
                file.write(f"\nGHL_REFRESH_TOKEN={refresh_token}\n")

        load_dotenv(override=True)
        interval = max(expires_in - 60, 3600)
        start_scheduler(interval)

        # Create HTML lines from token data
        token_html_lines = "".join([f"<p><strong>{key}</strong>: {value}</p>" for key, value in tokens.items()])

        html_content = f"""
            <h3>✅ Authorization successful!</h3>
            <p><strong>Access token acquired and refresh token saved.</strong></p>
            <h4>🔐 Token Details:</h4>
            {token_html_lines}
            <p>You may now close this window.</p>
        """
        return HTMLResponse(html_content)

    return HTMLResponse(f"<h3>❌ Token exchange failed</h3><p>{response.json()}</p>", status_code=400)

@app.get("/token")
def read_token():
    token = get_token()
    return {"access_token": token} if token else {"error": "Token not available"}

@app.get("/get-refresh-token")
async def get_refresh_token():
    try:
        await refresh_access_token()
        from token_manager import get_token  # refresh updates in memory
        return JSONResponse(
            {
                "success": True,
                "access_token": get_token()
            }
        )
    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "error": str(e)
            },
            status_code=500
        )