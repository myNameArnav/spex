import csv
import os
import requests
from sanitize_filename import sanitize
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USER_ID


# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYLISTS_URL = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"

# Replace with the desired scopes
SCOPE = "playlist-read-private"

# Create backup folder if it doesn't exist
backup_folder = "backup"
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)

# Get authorization code
auth_params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
}

auth_url = f'{AUTH_URL}?{"&".join([f"{k}={v}" for k, v in auth_params.items()])}'
print(f"Please authorize the application by visiting the following URL:\n{auth_url}\n")

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

if not access_token:
    error_message = token_data.get("error_description", "Access token not found.")
    print(f"Error retrieving access token: {error_message}")
    exit()

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

    print(f"Processing playlist: {playlist_name}")

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

    print(f'Playlist "{playlist_name}" exported to {csv_filepath}')

print("All playlists exported successfully.")
