import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN_DATA = {
    "access_token": None,
    "expires_at": 0,
}

def is_token_valid():
    return TOKEN_DATA["access_token"] and TOKEN_DATA["expires_at"] > time.time()

def get_token():
    return TOKEN_DATA["access_token"] if is_token_valid() else None
def _update_env_refresh_token(new_token):
    """Update the refresh token in the .env file (overwrite existing value)."""
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()

    with open(".env", "w") as f:
        found = False
        for line in lines:
            if line.startswith("GHL_REFRESH_TOKEN="):
                f.write(f"GHL_REFRESH_TOKEN={new_token}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"\nGHL_REFRESH_TOKEN={new_token}\n")

    print("🔁 .env file updated with new refresh token")
    load_dotenv(override=True)  # Refresh env vars

async def refresh_access_token():
    url = os.getenv("GHL_TOKEN_URL")
    payload = {
        "client_id": os.getenv("GHL_CLIENT_ID"),
        "client_secret": os.getenv("GHL_CLIENT_SECRET"),
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("GHL_REFRESH_TOKEN"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("\n📤 Sending token refresh request:")
    print("Payload:", payload)
    print("URL:", url)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload, headers=headers)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            print("❌ Response text:", response.text)
            raise
        data = response.json()
        TOKEN_DATA["access_token"] = data["access_token"]
        TOKEN_DATA["expires_at"] = time.time() + data["expires_in"] - 60
        print("✅ Access token refreshed!")

        # ✅ Update refresh token if it's returned (important!)
        if "refresh_token" in data:
            refresh_token = data["refresh_token"]
            _update_env_refresh_token(refresh_token)
