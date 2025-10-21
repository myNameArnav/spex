import csv
import os
import requests
import json
import argparse
import webbrowser
from datetime import datetime, timedelta
from sanitize_filename import sanitize
from dotenv import load_dotenv
from logger_config import setup_logging

# Set up logging
logger = setup_logging()
# load env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
USER_ID = os.getenv("USER_ID")

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI or not USER_ID:
    logger.error("Error: CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, or USER_ID is not set")
    exit(1)

# Token storage file
TOKEN_FILE = "spotify_tokens.json"

# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYLISTS_URL = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"

SCOPE = "playlist-read-private"

# Create backup folder if it doesn't exist
backup_folder = os.path.join("backup", datetime.now().strftime('%Y'), datetime.now().strftime('%m'), datetime.now().strftime('%d'))
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)


def save_tokens(access_token, refresh_token, expires_in):
    """Save tokens to file with expiration time"""
    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)


def load_tokens():
    """Load tokens from file"""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        return token_data
    except (json.JSONDecodeError, KeyError):
        return None


def is_token_expired(token_data):
    """Check if token is expired"""
    if not token_data:
        return True
    
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    # Refresh token 5 minutes before expiration
    return datetime.now() >= expires_at - timedelta(minutes=5)


def refresh_access_token(refresh_token):
    """Refresh access token using refresh token"""
    response = requests.post(
        TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token"), token_data.get("refresh_token", refresh_token), token_data.get("expires_in")
    else:
        logger.error(f"Error refreshing token: {response.text}")
        return None, None, None


def get_valid_access_token():
    """Get a valid access token, refreshing if necessary"""
    token_data = load_tokens()
    
    if not token_data or is_token_expired(token_data):
        if token_data and token_data.get("refresh_token"):
            logger.info("Token expired, refreshing...")
            access_token, refresh_token, expires_in = refresh_access_token(token_data["refresh_token"])
            if access_token:
                save_tokens(access_token, refresh_token, expires_in)
                return access_token
            else:
                logger.error("Failed to refresh token. Please re-authorize.")
                return None
        else:
            logger.error("No valid tokens found. Please run with --authorize flag first.")
            return None
    
    return token_data["access_token"]


def authorize_application():
    """Handle initial authorization flow"""
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    
    auth_url = f'{AUTH_URL}?{"&".join([f"{k}={v}" for k, v in auth_params.items()])}'
    logger.info(f"Please authorize the application by visiting the following URL:\n{auth_url}\n")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        logger.info("Browser opened automatically. If it didn't open, please copy the URL above.")
    except:
        logger.error("Could not open browser automatically. Please copy the URL above.")
    
    authorization_code = input("Enter the authorization code from the redirect URL: ")
    
    # Get access token using authorization code
    token_response = requests.post(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")
    
    if not access_token:
        error_message = token_data.get("error_description", "Access token not found.")
        logger.error(f"Error retrieving access token: {error_message}")
        return None
    
    # Save tokens for future use
    save_tokens(access_token, refresh_token, expires_in)
    logger.info("Authorization successful! Tokens saved for future use.")
    return access_token

def export_playlists(access_token):
    """Export all playlists to CSV files"""
    # Fetch user playlists
    playlists = []
    offset = 0
    limit = 50

    while True:
        playlists_response = requests.get(
            PLAYLISTS_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"offset": offset, "limit": limit},
        )

        playlists_data = playlists_response.json()
        playlists.extend(playlists_data["items"])

        if len(playlists_data["items"]) < limit:
            break

        offset += limit

    # Iterate over playlists
    for playlist in playlists:
        playlist_id = playlist["id"]
        playlist_name = playlist["name"]

        logger.info(f"Processing playlist: {playlist_name}")

        playlist_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        tracks = []
        offset = 0
        limit = 100

        while True:
            tracks_response = requests.get(
                playlist_tracks_url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"offset": offset, "limit": limit},
            )

            tracks_data = tracks_response.json()
            tracks.extend(tracks_data["items"])

            if len(tracks_data["items"]) < limit:
                break

            offset += limit

        # Sanitize playlist name for file name
        sanitized_playlist_name = sanitize(playlist_name)

        # Store tracks in a CSV file
        csv_filename = f"{sanitized_playlist_name}.csv"
        csv_filepath = os.path.join(backup_folder, csv_filename)

        with open(csv_filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Track Name", "Artist", "Album", "URL"])

            for track in tracks:
                try:
                    track_name = track["track"]["name"]
                    artist = track["track"]["artists"][0]["name"]
                    album = track["track"]["album"]["name"]
                    url = track["track"]["external_urls"]["spotify"]
                except:
                    continue

                writer.writerow([track_name, artist, album, url])

        logger.info(f'Playlist "{playlist_name}" exported to {csv_filepath}')

    logger.info("All playlists exported successfully.")


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Export Spotify playlists to CSV files")
    parser.add_argument("--authorize", action="store_true", 
                       help="Authorize the application (required for first run)")
    parser.add_argument("--headless", action="store_true", 
                       help="Run in headless mode (no interactive prompts)")
    
    args = parser.parse_args()
    
    if args.authorize:
        access_token = authorize_application()
        if not access_token:
            logger.error("Authorization failed. Exiting.")
            return
    else:
        access_token = get_valid_access_token()
        if not access_token:
            if args.headless:
                logger.error("No valid tokens found and running in headless mode. Exiting.")
                logger.error("Please run with --authorize flag first to authenticate.")
                return
            else:
                logger.info("No valid tokens found. Starting authorization process...")
                access_token = authorize_application()
                if not access_token:
                    logger.error("Authorization failed. Exiting.")
                    return
    
    # Export playlists
    export_playlists(access_token)


if __name__ == "__main__":
    main()
