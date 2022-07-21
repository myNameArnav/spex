import requests
import base64

global token


def postToken(clientID, secretID):
    """
    Sends POST request to Spotify to get a token using ```clientID``` and ```secretID```
    """

    data = clientID + ":" + secretID
    b64 = str(base64.b64encode(data.encode("utf-8")), "utf-8")
    url = "https://accounts.spotify.com/api/token"

    payload = "grant_type=client_credentials"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64}",
    }

    response = requests.request("POST", url, data=payload, headers=headers).json()
    token = response["access_token"]

    return token


def getPlaylists(limit, offset=0):
    """
    Sends GET request to Spotify to get all the user's playlists
    """

    url = f"https://api.spotify.com/v1/me/playlists"

    querystring = {"limit": limit, "offset": offset}

    payload = ""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    ).json()

    return response


def getSongs(playlistID, limit, offset):
    """
    Sends GET request to Spotify to get the playlist's songs using ```playlistID```
    """

    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"

    querystring = {"limit": limit, "offset": offset}

    payload = ""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    return response.text
