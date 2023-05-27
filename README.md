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

5. Rename a file named `config.py.sample` to `config.py` in the project directory.

6. Open `config.py` and add the following content, replacing the placeholder values with your actual Spotify API credentials

## Usage

1. Run the script using the following command: `python main.py`

2. The script will prompt you to authorize the application by visiting the provided authorization URL.

3. After authorizing the application, you will be redirected to the specified Redirect URI. Copy the authorization code from the URL. (ie the part after `?code=`)

4. Paste the authorization code into the script's prompt.

5. The script will fetch your playlists and save each playlist as a separate CSV file in the `backup` folder.

6. The CSV files will contain the track name, artist, album, and URL for each song in the playlist.

(Thanks GPT3.5)
