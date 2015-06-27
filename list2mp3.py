#-*- coding:utf-8 -*-
import youtube_dl

from apiclient.discovery import build
from apiclient.errors import HttpError

import sys
import json

class YoutubeSearch(object):
    """template class for use search"""
    video_id = ''
    title = ''
    def __init__(self, video_id, title):
        self.video_id = video_id
        self.title = title

DEVELOPER_KEY = "AIzaSyByJz9GoByvy373JJ1R8cCD3W7cBiox_MQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def search_video(title):
    search_response = youtube.search().list(
        q=title,
        part="id,snippet",
        maxResults=10
    ).execute()
    with open('dumb.txt', 'w') as jsonf:
        jsonf.write(json.dumps(search_response)) 
    search_array = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            tmp = YoutubeSearch(search_result["id"]["videoId"], search_result["snippet"]["title"])
            search_array.append(tmp)
    return search_array

# youtube_dl configuration
class MyLogger(object):

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading... ETA: ' + str(d["eta"]) + " seconds")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to mp3')
        sys.stdout.flush()

ydl_opts = {
    'format': 'bestaudio',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


# main
if __name__ == "__main__":
    youtube = build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    print
    print("Reading file 'titles.txt'.")
    with open("titles.txt") as f:

        titles = []
        for line in f:
            line = line.strip()
            if len(line) > 0:
                titles.append(line)

        lenTitles = len(titles)
        print("Total titles: " + str(lenTitles))
        print
        for i, title in enumerate(titles):
            print("(" + str(i + 1) + "/" + str(lenTitles) + ") " + title)
            print("\tSearching video")
            try:
                videos = search_video(title)
                for video in videos:
                    print("\tFound video: '" + video.title + "' - ID: " + video.video_id)
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download(['http://www.youtube.com/watch?v=' + video.video_id])
                        print("\tDone")
            except HttpError, e:
                print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

        print("All titles downloaded and converted")
