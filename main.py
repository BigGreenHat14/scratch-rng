import scratchattach as sa # pyright: ignore[reportMissingImports]
import signal
import sys
import random
from io import BytesIO
from typing import Optional
import time
import requests
from PIL import Image

# Login once, synchronously
session = sa.login_by_id("session_id_here", username="crashbandicootsthe1")
conn = session.connect_cloud("1180630143")
client = conn.requests()

# HTTP session for profile image requests
_http_session = requests.Session()


def get_random_user() -> Optional[sa.User]:
    """Find a random user by probing for a valid project."""
    user = session.connect_user_by_id(random.randint(1, 159767440))
    print("Found User",user.id)
    return user


def fetch_profile_hex(user: sa.User) -> str:
    """Downloads avatar, converts to 50x50 RGB hex string."""
    url = f"https://uploads.scratch.mit.edu/get_image/user/{user.id}_24x24.png"
    resp = _http_session.get(url)
    resp.raise_for_status()
    data = resp.content

    image = Image.open(BytesIO(data)).resize((50, 50), Image.LANCZOS).convert("RGB")
    return image.tobytes().hex().upper()


@client.request
def ping() -> str:
    print("Ping received")
    return "pong"


@client.request
def roll() -> list[str]:
    user = get_random_user()
    if user is None:
        return ["", "Shutdown"]
    hex_str = fetch_profile_hex(user)
    print(f"Fetched {len(hex_str)} hex chars for {user.username!r}")
    return [hex_str, user.username]


@client.event
def on_ready() -> None:
    print("Client is ready and awaiting requests")


if __name__ == "__main__":
    client.start(thread=False)
