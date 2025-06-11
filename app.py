from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from functions import get_weather, determine_song, create_spotify_playlist
from keys import spotify_client_id, spotify_client_secret

app = Flask(__name__)
app.secret_key = "a_permanent_and_super_secret_key"

oauth = OAuth(app)
oauth.register(
    name="spotify",
    client_id=spotify_client_id,
    client_secret=spotify_client_secret,
    authorize_url="https://accounts.spotify.com/authorize",
    access_token_url="https://accounts.spotify.com/api/token",
    api_base_url="https://api.spotify.com/v1/",
    client_kwargs={
        'scope': 'playlist-modify-private playlist-modify-public',
    }
)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate', methods=['POST'])
def generate():
    place = request.form.get('location')
    num_songs = int(request.form.get('num_songs', 10))

    weather_data = get_weather(place)
    if not weather_data:
        return render_template('error.html', error="Weather data not found for that location.")

    temp, weather_type = weather_data
    songs = determine_song(temp, weather_type, num_songs)
    if not songs:
        return render_template('error.html', error="No songs matched the weather criteria.")

    session['songs'] = songs
    session['place'] = place

    return render_template("result.html", location=place, songs=songs, temp=round(temp), type=weather_type)


@app.route('/login')
def login():
    # This route sends the user to Spotify to authorize the app.
    redirect_uri = url_for('authorize', _external=True)
    return oauth.spotify.authorize_redirect(redirect_uri)


@app.route('/spotifyauthorize')
def authorize():
    token = oauth.spotify.authorize_access_token()

    songs = session.get('songs')
    place = session.get('place')

    if not songs or not place:
        return render_template('error.html', error="Missing session data.")

    client = oauth.spotify
    client.token = token

    playlist_id = create_spotify_playlist(songs, f"Weather Vibes in {place}", client)

    session.pop('songs', None)
    session.pop('place', None)

    if not playlist_id:
        return render_template("error.html", error="Failed to create the Spotify playlist.")

    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    return render_template('success.html', playlist_url=playlist_url)


if __name__ == '__main__':
    app.run(debug=True)