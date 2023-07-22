# importing libraries
from bs4 import BeautifulSoup
import requests
import smtplib
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# DATE INPUT
time = input("Enter date in the format YYYY-MM-DD")

#SCRAPING THE DATA AND PARSING IN HTML FORMAT
response = requests.get(f"https://www.billboard.com/charts/hot-100/{time}")
billPage = response.text
soup = BeautifulSoup(billPage, 'html.parser')

top_songs = soup.select("li.o-chart-results-list__item h3#title-of-a-story")

#STORING TOP SONGS
song_title = []
for i in top_songs:
    song_title.append(i.text.strip())

song_list = f''' {', '.join(song_title)}'''
print(song_list)

# MAILING THE SONG LIST USING smtplib
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login('Sender Mail Address', 'APP PASSWORD')  #APP PASSWORD has to be set in google settings for the account in order to send the mail through python
    smtp.sendmail('Sender Mail Address', 'Receiver Mail Address', song_list)

clientid = "Your Client ID"
clientsecret = "Your Client Secret "   #Client ID and Client Secret you get after you create a new app on Spotify developer dashboard

# SPOTIFY AUTHORIZATION
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="playlist-modify-private",
    client_id=clientid,
    client_secret=clientsecret,
    redirect_uri="https://example.com/",
    cache_path="./token.txt",
    show_dialog=True,
)
)

#SEARCHING FOR SONGS USING THE API
song_uri_list = []
for songs in song_title:
    res = sp.search(q=songs, limit=5, type="track")
    search_res = res['tracks']['items']

    i = 0
    t_flag = False
    for song in search_res:
        if (songs.lower() in song['name'].lower() and not t_flag):
            song_uri_list.append(song["uri"])
            t_flag = True
        else:
            i += 1

    if i == 5:
        print(songs, "Not found.")

print(len(song_uri_list))

#ADDING THE SONGS TO THE PLAYLIST
my_playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=f"{time} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=my_playlist['id'], items=song_uri_list)
