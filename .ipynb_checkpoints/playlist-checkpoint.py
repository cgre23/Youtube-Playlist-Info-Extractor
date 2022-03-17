#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Created on Tue Mar 15 20:17:53 2022

@author: christiangrech
"""

""" Pull All Youtube Videos from a Playlist """

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import urllib
import isodate
import datetime
import pandas as pd

keys_file = open("key.txt") # INSERT DEVELOPER KEY IN THIS TEXT FILE
lines = keys_file.readlines()

PLAYLIST_ID = "PLAYLIST_ID"
DEVELOPER_KEY = lines[0].rstrip()
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def fetch_all_youtube_videos(playlistId):
    """
    Fetches a playlist of videos from youtube
    We splice the results together in no particular order

    Parameters:
        parm1 - (string) playlistId
    Returns:
        playListItem Dict
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    res = youtube.playlistItems().list(
    part="contentDetails",
    playlistId=playlistId,
    maxResults="50"
    ).execute()

    nextPageToken = res.get('nextPageToken')
    while ('nextPageToken' in res):
        nextPage = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlistId,
        maxResults="50",
        pageToken=nextPageToken
        ).execute()
        res['items'] = res['items'] + nextPage['items']

        if 'nextPageToken' not in nextPage:
            res.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']

    return res

if __name__ == '__main__':
    
  # comedy central playlist, has 332 video
  # https://www.youtube.com/watch?v=tJDLdxYKh3k&list=PLD7nPL1U-R5rDpeH95XsK0qwJHLTS3tNT
    info = {}
    info['links'] = []
    info['duration'] = []
    total_dur = datetime.timedelta(0)
    videos = fetch_all_youtube_videos(PLAYLIST_ID)
    for video in videos['items']:
        video_id = video['contentDetails']['videoId']
        url = f'https://www.youtube.com/watch?v={video_id}'
        search_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={DEVELOPER_KEY}&part=contentDetails'
        req = urllib.request.Request(search_url)
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        all_data = data['items']
        info['links'].append(url)
        dur= all_data[0]['contentDetails']['duration']
        duration = isodate.parse_duration(dur)
        total_dur = total_dur + duration
        info['duration'].append(str(duration))
    
df = pd.DataFrame(data=info)
df.to_excel('/Users/christiangrech/Downloads/dict1.xlsx')
    