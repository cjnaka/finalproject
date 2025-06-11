from authlib.integrations.requests_client import OAuth2Session
from keys import spotify_client_id, spotify_client_secret

scope = "playlist-modify-public playlist-modify-private"
authorization_endpoint = "https://accounts.spotify.com/authorize"
token_endpoint = "https://accounts.spotify.com/api/token"
api_endpoint = "https://api.spotify.com/v1"

def authenticate_client():
    client = OAuth2Session(
        spotify_client_id,
        spotify_client_secret,
        scope=scope,
        redirect_uri = "https://carsonakagawara.pythonanywhere.com"
    )

    uri,state = client.create_authorization_url(authorization_endpoint)
    print(f"Go to this URL: {uri}")

    authorization_response = input("Paste redirect URL here: ")

    token = client.fetch_token(token_endpoint, authorization_response=authorization_response)

    return client