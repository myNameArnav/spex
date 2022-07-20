import requests


def getResponse():
    """
    Sends API call to Spotify to get all the user's playlists
    """
    from secret import token

    url = "https://api.spotify.com/v1/me/playlists"

    payload = ""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request("GET", url, data=payload, headers=headers)

    return response.text

print(getResponse())