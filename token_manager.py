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
