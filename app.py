import requests
from secret import token

url = "https://api.spotify.com/v1/me/playlists"

payload = ""
headers = {"Authorization": f"Bearer {token}"}

response = requests.request("GET", url, data=payload, headers=headers)

print(response.text)