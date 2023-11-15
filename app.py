# Main.py
import spotipy
import json
from flask import Flask, render_template, Response
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Konfigurasi otorisasi
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
  client_id="YOUR_CLIENT_ID",
  client_secret="YOUR_CLIENT_SECRET",
  redirect_uri="http://localhost:8888/callback",
  scope="user-read-playback-state"
))

# Fungsi untuk mengirim data SSE
def generate():
  while True:
    try:
      current_playback = sp.current_playback()

      if current_playback is not None and current_playback.get("is_playing", False):
        if current_playback["currently_playing_type"] == "ad":
          # Tampilkan pesan offline saat memutar iklan
          data = {
            "is_playing": False,
            "ad_playing": True
          }
        else:
          track_name = current_playback["item"]["name"]
          artist_name = current_playback["item"]["artists"][0]["name"]
          album_image_url = current_playback["item"]["album"]["images"][0]["url"]
          data = {
            "is_playing": True,
            "ad_playing": False,
            "track_name": track_name,
            "artist_name": artist_name,
            "album_image_url": album_image_url
          }
      else:
        track_name = "Tidak ada lagu yang sedang diputar"
        artist_name = ""
        album_image_url = ""
        data = {
          "is_playing": False,
          "ad_playing": False,
          "track_name": track_name,
          "artist_name": artist_name,
          "album_image_url": album_image_url
        }

    except Exception as e:
      # Tangani kesalahan jika ada
      data = {
        "error": str(e)
      }

    yield f"data: {json.dumps(data)}\n\n"

@app.route("/")
def index():
  current_playback = sp.current_playback()
  is_playing = False

  if current_playback is not None and current_playback["is_playing"]:
    is_playing = True

  return render_template("index.html", is_playing=is_playing, current_playback=current_playback)

@app.route("/events")
def sse():
  return Response(generate(), content_type="text/event-stream")

if __name__ == "__main__":
  app.run(debug=True)
