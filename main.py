import scratchattach as sa
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
    author = None
    while not author:
        project_id = random.randint(100_000_000, 1_100_000_000)
        try:
            project = sa.get_project(project_id)
            # Check if project is valid
            if isinstance(project, (sa.Project)):
                author = project.author()
                print(f"Found project {project_id}, author={author.username!r}")
                return author
        except sa.utils.exceptions.ProjectNotFound:
            continue
    return None


def fetch_profile_hex(user: sa.User) -> str:
    """Downloads avatar, converts to 24x24 RGB hex string."""
    url = f"https://uploads.scratch.mit.edu/get_image/user/{user.id}_24x24.png"
    resp = _http_session.get(url)
    resp.raise_for_status()
    data = resp.content

    image = Image.open(BytesIO(data)).resize((24, 24), Image.LANCZOS).convert("RGB")
    return image.tobytes().hex().upper()


@client.request
def ping() -> str:
    print("Ping request received")
    return "pong"


@client.request
def roll() -> list[str]:
    user = get_random_user()
    if user is None:
        return ["", "Error caught"]
    hex_str = fetch_profile_hex(user)
    print(f"Fetched {len(hex_str)} hex chars for {user.username!r}")
    return [hex_str, user.username]


@client.event
def on_ready() -> None:
    print("Client is ready and awaiting requests")


if __name__ == "__main__":
    client.start()
    while True:
        time.sleep(5)
