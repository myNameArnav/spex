# Spotify Playlist EXporter AKA Spex

This script allows you to export your Spotify playlists as CSV files, including the track name, artist, album, and URL.

## Setup

1. Clone or download this repository to your local machine.

2. (Optional) Make virtual environment

3. Install the required dependencies by running the following command: `pip install -r requirements.txt`

4. Obtain Spotify API credentials:

    - Create a Spotify Developer account at [https://developer.spotify.com/](https://developer.spotify.com/).

    - Create a new Spotify application to get the Client ID and Client Secret.

    - Set the Redirect URI to a valid URI (e.g., [https://developer.spotify.com/](https://developer.spotify.com/)).

    - Note down the Client ID, Client Secret, and Redirect URI.

5. Create a `.env` file in the project directory with your Spotify API credentials:

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=your_redirect_uri_here
USER_ID=your_spotify_username_here
```

## Usage

### First-time Setup (Authorization Required)

1. Run the script with the `--authorize` flag: `python main.py --authorize`

2. The script will automatically open your browser to the Spotify authorization page.

3. After authorizing the application, you will be redirected to the specified Redirect URI. Copy the authorization code from the URL (the part after `?code=`).

4. Paste the authorization code into the script's prompt.

5. The script will save your tokens for future use and export your playlists.

### Subsequent Runs (Headless Mode)

Once authorized, you can run the script in headless mode:

- **Interactive mode**: `python main.py` (will prompt for authorization if tokens are expired)
- **Headless mode**: `python main.py --headless` (will exit if tokens are expired, requiring manual re-authorization)

### Output

The script will fetch your playlists and save each playlist as a separate CSV file in the `backup` folder. The CSV files will contain the track name, artist, album, and URL for each song in the playlist.

### Command Line Options

- `--authorize`: Force authorization flow (required for first run)
- `--headless`: Run in headless mode (no interactive prompts)
