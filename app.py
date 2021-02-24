from flask import Flask, request, redirect, g, render_template, session, flash
from spotify_requests import spotify
import startup

app = Flask(__name__)
app.secret_key = ''

# ----------------------- AUTH API PROCEDURE -------------------------

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)

@app.route("/callback/")
def callback():

    flash('Login Succesful!')
    auth_token = request.args.get('code')
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return render_template('home.html')

def valid_token(resp):
    return resp is not None and not 'error' in resp

# -------------------------- API REQUESTS ----------------------------

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        # get profile data
        profile_data = spotify.get_users_profile(auth_header)

        # get user playlist data
        playlist_data = spotify.get_users_playlists(auth_header)
        
        # get user recently played tracks
        recently_played = spotify.get_users_recently_played(auth_header)

        # get user top artists
        top_artists= spotify.get_users_top(auth_header, 'artists')

        if valid_token(top_artists):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data["items"],
                               recently_played=recently_played["items"],
                               top_artists=top_artists["items"])

    return render_template('profile.html')

@app.route('/playlists')
def playlists():
#     if 'auth_header' in session:
#         auth_header = session['auth_header']

#         limit = request.args['limit']
#         seed_genres = request.args['seed_genres']
#         target_danceability = request.args['target_danceability']

#         data = spotify.make_playlists(auth_header, limit, seed_genres, target_danceability)
     return render_template('playlists.html')


@app.route('/search/')
def search():
    try:
        search_type = request.args['search_type']
        name = request.args['name']
        return make_search(search_type, name)
    except:
        return render_template('search.html')


@app.route('/search/<search_type>/<name>')
def search_item(search_type, name):
    return make_search(search_type, name)


def make_search(search_type, name):
    if search_type not in ['artist', 'album', 'playlist', 'track']:
        return render_template('index.html')

    data = spotify.search(search_type, name)
    api_url = data[search_type + 's']['href']
    items = data[search_type + 's']['items']

    return render_template('search.html',
                           name=name,
                           results=items,
                           api_url=api_url,
                           search_type=search_type)

@app.route('/artist/<id>')
def artist(id):
    artist = spotify.get_artist(id)

    if artist['images']:
        image_url = artist['images'][0]['url']
    else:
        image_url = 'http://bit.ly/2nXRRfX'

    tracksdata = spotify.get_artist_top_tracks(id)
    tracks = tracksdata['tracks']

    related = spotify.get_related_artists(id)
    related = related['artists']

    return render_template('artist.html',
                           artist=artist,
                           related_artists=related,
                           image_url=image_url,
                           tracks=tracks)

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        flash('You have been logged out', "info")
        session.pop(key)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)