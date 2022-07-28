#!/usr/bin/python

# River's Spotify Playlist Helper!
# The purpose of this program is to help you organise your Spotify playlists by
# allowing you to set a time of day that you want to start your playlist, and
# using that data to tell you at what time each song will start and finish
# it will also take into account the length of your crossfade
# I haven't decided on a license yet, so this code is copyright River Wicks
# until I can decide on an appropriate license.

import json
import spotipy
import spotipy.util as util
import time
import difflib
import os

#Assigning variables.
MS = 1000
tracklist = []

def get_sec(time_str): #stolen straight from StackExchange: https://stackoverflow.com/a/6402859/7980598
    h, m, s = time_str.split(':')
    return int(h)*3600 + int(m)*60 + int(s)

def format_time(time_sec):
    return time.strftime('%H:%M:%S', time.gmtime(time_sec))

with open("config.txt", "r") as user_data:
    username = user_data.readline().partition('#')[0].rstrip()      # The user's username should be the first line of the user_data file
    playlist_id = user_data.readline().partition('#')[0].rstrip()   # Playlist ID is the second line in the user_data file
    scope = user_data.readline().partition('#')[0].rstrip()         # Scopes are the third line of the file
    start_time = user_data.readline().partition('#')[0].rstrip()    # Gets the start time in hh:mm:ss format
    start_time = get_sec(start_time)                                # Converts start time to seconds
    current_time = start_time
    crossfade_length = int(user_data.readline().partition('#')[0].rstrip())
with open("app_data.txt", "r") as app_data:
    client_id = app_data.readline().rstrip()        # Client ID is the first line of the app_data file
    client_secret = app_data.readline().rstrip()    # Client secret is the second line of the app_data file
    redirect_uri = app_data.readline().rstrip()     # Don't know what to do with this, tbh. But it's in there. It's the third line of the app_data file

token = util.prompt_for_user_token(username,scope,client_id,client_secret,redirect_uri)
sp = spotipy.Spotify(auth=token)

class Song(object):
    def __init__(self, name, artists, duration_ms, song_uri, length):
        self.name = name
        self.artists = artists
        self.duration_ms = duration_ms
        self.song_uri = song_uri
        self.length = length

def add_tracks_to_list(tracks):
    for item in tracks['items']:
        track = item['track']
        name = track['name']
        artists = []
        for arti in track['artists']:
            artists.append(arti['name'])
        duration_ms = track['duration_ms']
        song_uri = track['uri']
        length = format_time(duration_ms/MS)
        tracklist.append(Song(name,artists,duration_ms,song_uri,length))


def get_tracks():
    results = sp.user_playlist(username, playlist_id, fields="tracks,next")
    tracks = results['tracks']
    add_tracks_to_list(tracks)
    while tracks['next']:       #this checks if there are more than 100 tracks (as 'tracks' will only contain the first 100 songs)
        tracks = sp.next(tracks)    #if there are more than 100 tracks, the next 100 are assigned to 'tracks'
        add_tracks_to_list(tracks)  #then tracks is passed to add_tracks_to_list() to add them to the list


def print_tracks():
    get_tracks()
    current_time = start_time
    n = 0
    for item in tracklist:
        print("{}: {}".format(n,item.name))
        end_time = current_time + (item.duration_ms/MS)
        print("Time: {} to {}".format(format_time(current_time), format_time(end_time)))
        current_time += (item.duration_ms/MS) - crossfade_length
        n+=1
    print("Playlist ends:   {}".format(format_time(current_time)))
    print("Total tracks:    {}".format(n))

def move_track():
    #Use this guide: https://beta.developer.spotify.com/console/put-playlist-tracks/
    while True:
        word_to_search = input("Type the name of the track you want to move: ")
        matches = difflib.get_close_matches(word_to_search, (item.name for item in playlist_tracks))
        if len(matches) == 0:
            matches = []
            for item in playlist_tracks:
                if item.name.startswith(word_to_search, beg=0):
                    matches.add(item.name)
            if len(matches) == 0:
                print("No results found for {}. Please try another search.".format(word_to_search))
            elif len(matches) == 1:
                track_to_move = matches[0]
            elif len(matches) > 1:
                print("Multiple results for {}. Please specify which one you want.".format(word_to_search))
                print(matches)
        elif len(matches) > 1:
            print("Multiple results for {}. Please specify which one you want.".format(word_to_search))
            print(matches)
        else:
            track_to_move = matches[0]
            break
    new_location = int(input("Please enter the position you wish to move \"{}\" to: ".format(track_to_move)))
    for item in playlist_tracks:
        if item.name == track_to_move:
            sp.user_playlist_reorder_tracks(username, playlist_id, item.location, new_location)
    print("Moving track {} to position {}".format(track_to_move, new_location))
def find_uri():
    track_pos = int(input("Please enter the position of the track you want the URI for: "))
    for item in playlist_tracks:
        if item['position'] == track_pos:
            track_uri = item['uri']
            break
    print(track_uri)
def main_menu():
    while True:
        print(  "1. List tracks" + "\n" +
                "2. Move track" + "\n" +
                "3. Exit")
        answer = input()
        if not answer.isdigit():
            print("Please enter a valid option")
        else:
            answer = int(answer)
            if answer > 3 or answer == 0:
                print("Please enter a valid option")
            elif answer==1:
                print_tracks()
            elif answer==2:
                move_track()
            elif answer==3:
                os._exit(0)
main_menu()
