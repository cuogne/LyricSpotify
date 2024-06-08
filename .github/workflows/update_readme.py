import os
import requests
from bs4 import BeautifulSoup
import base64

def get_spotify_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
    
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {b64_auth_str}"
        },
        data={
            "grant_type": "client_credentials"
        }
    )
    return response.json().get("access_token")

def get_current_playing_song(token):
    response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    if response.status_code == 204 or response.json() == {}:
        return None
    return response.json()

def get_genius_token():
    return os.getenv("GENIUS_TOKEN")

def search_genius_song(song_name, artist_name, token):
    search_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"{song_name} {artist_name}"}
    
    response = requests.get(search_url, headers=headers, params=params)
    return response.json()

def get_lyrics_url(song_id, token):
    song_url = f"https://api.genius.com/songs/{song_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(song_url, headers=headers)
    return response.json()["response"]["song"]["url"]

def scrape_lyrics(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    lyrics = soup.find("div", class_="lyrics").get_text()
    return lyrics

def update_readme(song_name, artist_name, lyrics):
    spotify_widget = """
<div align="center">
  <a href="https://spotify-github-profile.vercel.app/api/view?uid=31z4hwucc4g3x3klr2ezheobh2ee&redirect=true">
    <img align="center" src="https://spotify-github-profile.vercel.app/api/view?uid=31z4hwucc4g3x3klr2ezheobh2ee&cover_image=true&theme=natemoo-re&show_offline=true&background_color=121212&interchange=true&bar_color=53b14f&bar_color_cover=false" alt="Spotify Now Playing" width="400">
  </a>
</div>
"""
    
    readme_content = f"""
{spotify_widget}

### Now Playing 🎧
**{song_name}** by **{artist_name}**

#### Lyrics:
{lyrics}
"""

    with open("README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_token = get_spotify_token(client_id, client_secret)
    
    song_info = get_current_playing_song(spotify_token)
    if song_info:
        if 'item' in song_info:
            song_name = song_info['item']['name']
            artist_name = song_info['item']['artists'][0]['name']
            
            genius_token = get_genius_token()
            song_search = search_genius_song(song_name, artist_name, genius_token)
            
            if song_search["response"]["hits"]:
                song_id = song_search["response"]["hits"][0]["result"]["id"]
                lyrics_url = get_lyrics_url(song_id, genius_token)
                lyrics = scrape_lyrics(lyrics_url)
                
                update_readme(song_name, artist_name, lyrics)
            else:
                print("Lyrics not found")
        else:
            print("No 'item' key in response")
    else:
        print("No song currently playing")
