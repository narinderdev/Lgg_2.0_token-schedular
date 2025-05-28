# from fastapi import FastAPI
# from token_manager import refresh_access_token, get_token
# from scheduler import start_scheduler  # <-- import the scheduler

# app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     await refresh_access_token()  # Immediate token refresh at startup
#     start_scheduler()             # Start the 23-hour scheduler

# @app.get("/token")
# def read_token():
#     token = get_token()
#     return {"access_token": token} if token else {"error": "Token not available"}
# from fastapi import FastAPI, Request
# import os
# import requests
# from dotenv import load_dotenv
# from scheduler import start_scheduler
# from token_manager import refresh_access_token, get_token
# from fastapi.responses import RedirectResponse
# load_dotenv()
# app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     await refresh_access_token()
#     start_scheduler()
# @app.get("/")
# def root():
#     return {"message": "GHL Token Manager is running"}

# @app.get("/token")
# def read_token():
#     token = get_token()
#     return {"access_token": token} if token else {"error": "Token not available"}
# from fastapi.responses import RedirectResponse

# @app.get("/auth")
# def redirect_to_ghl():
#     base_url = "https://marketplace.leadconnectorhq.com/oauth/chooselocation"
#     client_id = os.getenv("GHL_CLIENT_ID")
#     redirect_uri = os.getenv("GHL_REDIRECT_URI")
#     scopes = "contacts.readonly calendars.readonly campaigns.readonly"

#     redirect_url = (
#         f"{base_url}?"
#         f"response_type=code"
#         f"&client_id={client_id}"
#         f"&redirect_uri={redirect_uri}"
#         f"&scope={scopes}"
#     )

#     return RedirectResponse(url=redirect_url)

# @app.get("/auth/callback")
# def auth_callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return {"error": "Authorization code missing"}

#     payload = {
#         "grant_type": "authorization_code",
#         "client_id": os.getenv("GHL_CLIENT_ID"),
#         "client_secret": os.getenv("GHL_CLIENT_SECRET"),
#         "code": code,
#         "redirect_uri": os.getenv("GHL_REDIRECT_URI")
#     }

#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     response = requests.post(os.getenv("GHL_TOKEN_URL"), data=payload, headers=headers)

#     if response.status_code == 200:
#         tokens = response.json()
#         access_token = tokens["access_token"]
#         refresh_token = tokens["refresh_token"]

#         # OPTIONAL: Save the refresh_token to a .env file (or separate file securely)
#         with open(".env", "a") as f:
#             f.write(f"\nGHL_REFRESH_TOKEN={refresh_token}")

#         return {
#             "message": "✅ Authorization successful.",
#             "access_token": access_token,
#             "refresh_token": refresh_token
#         }
#     else:
#         return {
#             "error": "Token exchange failed",
#             "details": response.json()
#         }
from fastapi import FastAPI, Request
import os
import requests
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from scheduler import start_scheduler
from token_manager import refresh_access_token, get_token
from fastapi.responses import HTMLResponse
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

@app.get("/")
def root():
    return {"message": "GHL Token Manager is running. Go to /auth to begin."}

@app.get("/token")
def read_token():
    token = get_token()
    return {"access_token": token} if token else {"error": "Token not available"}

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

        with open(".env", "a") as f:
            f.write(f"\nGHL_REFRESH_TOKEN={refresh_token}")

        load_dotenv(override=True)
        start_scheduler()

        return HTMLResponse(f"<h3>✅ Authorization successful!</h3><p>Refresh token saved. You may close this window.</p>")
    else:
        return HTMLResponse(f"<h3>❌ Token exchange failed</h3><p>{response.json()}</p>", status_code=400)
