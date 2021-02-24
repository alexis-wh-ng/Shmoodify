import json
import requests
from urllib.parse import quote

'''
    --------------------- CONTENTS --------------------
    1. AUTHORIZATION
    2. USER PROFILE

    2. ARTISTS
    3. SEARCH
    4. USER RELATED REQUETS (NEEDS OAUTH)
    5. ALBUMS
    6. USERS
    7. TRACKS
'''

# ----------------- 1. AUTHORIZATION -------------------

# Spotify URLS
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = 'https://api.spotify.com/v1'
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Client Keys
CLIENT_ID = ''
CLIENT_SECRET = ''

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "http://127.0.0.1:5000/callback/"
SCOPE = "playlist-modify-public playlist-modify-private user-read-recently-played user-top-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# https://developer.spotify.com/documentation/general/guides/authorization-guide/
auth_query_parameters = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "state": STATE,
    "show_dialog": SHOW_DIALOG_str,
}

# Authorization
URL_ARGS = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
AUTH_URL = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS)

def authorize(auth_token):

    #Requests refresh and access tokens
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Tokens are returned to application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Use access token to access Spotify API
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    return auth_header

# ------------------ 2. USER PROFILE  -------------------- #

# Profile Data
USER_PROFILE_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'me')
USER_PLAYLISTS_ENDPOINT = "{}/{}".format(USER_PROFILE_ENDPOINT, 'playlists')
USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT = "{}/{}".format(USER_PROFILE_ENDPOINT, 'top')  # /<type>
USER_RECENTLY_PLAYED_ENDPOINT = "{}/{}/{}".format(USER_PROFILE_ENDPOINT,'player', 'recently-played')
BROWSE_FEATURED_PLAYLISTS = "{}/{}/{}".format(SPOTIFY_API_URL, 'browse','featured-playlists')

def get_users_profile(auth_header):
    url = USER_PROFILE_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_users_playlists(auth_header):
    url = USER_PLAYLISTS_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_users_top(auth_header, t):
    if t not in ['artists', 'tracks']:
        print('invalid type')
        return None
    url = "{}/{type}".format(USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT, type=t)
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_users_recently_played(auth_header):
    url = USER_RECENTLY_PLAYED_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_featured_playlists(auth_header):
    url = BROWSE_FEATURED_PLAYLISTS
    resp = requests.get(url, headers=auth_header)
    return resp.json()

# ----------------- 2. SEARCH ------------------------
# https://developer.spotify.com/web-api/search-item/

SEARCH_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'search')

# https://developer.spotify.com/web-api/search-item/

def search(search_type, name):
    if search_type not in ['artist', 'track', 'album', 'playlist']:
        print('invalid type')
        return None

    # query = f'{SEARCH_ENDPOINT}?name={name}&search_type={search_type}'
    # resp = requests.get(query)
    
    myparams = {'type': search_type}
    myparams['q'] = name
    resp = requests.get(SEARCH_ENDPOINT, params=myparams)

    return resp.json()

# # ---------------- 2. PLAYLISTS ------------------------
# PLAYLISTS_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'recommendations?')

# # #filters
# # limit = 10
# market = "US"
# # seed_genres = "indie"
# # target_danceability = 0.9

# def make_playlists(auth_header, limit, seed_genres, target_danceability):
    
#     #make invalid statement

#     query = f'{PLAYLISTS_ENDPOINT}limit={limit}&market={market}&seed_genres={seed_genres}&target_danceability={target_danceability}'
#     resp = requests.get(query, headers = auth_header)
#     json_response = resp.json()

#     for i in json_response['tracks']:
#         uris.append(i)
#         return (f"\"{i['name']}\" by {i['artists'][0]['name']}")


# ---------------- 2. ARTISTS ------------------------
# https://developer.spotify.com/web-api/artist-endpoints/

GET_ARTIST_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'artists')  # /<id>


# https://developer.spotify.com/web-api/get-artist/
def get_artist(artist_id):
    url = "{}/{id}".format(GET_ARTIST_ENDPOINT, id=artist_id)
    resp = requests.get(url)
    return resp.json()


# https://developer.spotify.com/web-api/get-several-artists/
def get_several_artists(list_of_ids):
    url = "{}/?ids={ids}".format(GET_ARTIST_ENDPOINT, ids=','.join(list_of_ids))
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-artists-albums/
def get_artists_albums(artist_id):
    url = "{}/{id}/albums".format(GET_ARTIST_ENDPOINT, id=artist_id)
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-artists-top-tracks/
def get_artists_top_tracks(artist_id, country='US'):
    url = "{}/{id}/top-tracks".format(GET_ARTIST_ENDPOINT, id=artist_id)
    myparams = {'country': country}
    resp = requests.get(url, params=myparams)
    return resp.json()

# https://developer.spotify.com/web-api/get-related-artists/
def get_related_artists(artist_id):
    url = "{}/{id}/related-artists".format(GET_ARTIST_ENDPOINT, id=artist_id)
    resp = requests.get(url)
    return resp.json()



# ---------------- 5. ALBUMS ------------------------
# https://developer.spotify.com/web-api/album-endpoints/

GET_ALBUM_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'albums')  # /<id>

# https://developer.spotify.com/web-api/get-album/
def get_album(album_id):
    url = "{}/{id}".format(GET_ALBUM_ENDPOINT, id=album_id)
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-several-albums/
def get_several_albums(list_of_ids):
    url = "{}/?ids={ids}".format(GET_ALBUM_ENDPOINT, ids=','.join(list_of_ids))
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-albums-tracks/
def get_albums_tracks(album_id):
    url = "{}/{id}/tracks".format(GET_ALBUM_ENDPOINT, id=album_id)
    resp = requests.get(url)
    return resp.json()

# ------------------ 6. USERS ---------------------------
# https://developer.spotify.com/web-api/user-profile-endpoints/

GET_USER_ENDPOINT = '{}/{}'.format(SPOTIFY_API_URL, 'users')

# https://developer.spotify.com/web-api/get-users-profile/
def get_user_profile(user_id):
    url = "{}/{id}".format(GET_USER_ENDPOINT, id=user_id)
    resp = requests.get(url)
    return resp.json()

# ---------------- 7. TRACKS ------------------------
# https://developer.spotify.com/web-api/track-endpoints/

GET_TRACK_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'tracks')  # /<id>

# https://developer.spotify.com/web-api/get-track/
def get_track(track_id):
    url = "{}/{id}".format(GET_TRACK_ENDPOINT, id=track_id)
    resp = requests.get(url)
    return resp.json()

# https://developer.spotify.com/web-api/get-several-tracks/
def get_several_tracks(list_of_ids):
    url = "{}/?ids={ids}".format(GET_TRACK_ENDPOINT, ids=','.join(list_of_ids))
    resp = requests.get(url)
    return resp.json()





