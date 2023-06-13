import os
import pickle
import json

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request

scopes = ["https://www.googleapis.com/auth/youtube"]


def main():
    with open("likedVideosIds.json", 'r') as videos_file:
        videos = json.load(videos_file)

    print(videos)

    credentials = None

    if os.path.exists("token.pickle"):
        # load saved creds from file
        with open("token.pickle", 'rb') as token:
            credentials = pickle.load(token)
    # if the credentials aren't valid or don't exist, use the refresh token or oauth to log in
    if not credentials or not credentials.valid:
        # if they're expired, use the refresh token
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # connects to secrets file for oauth authentication
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
            flow.run_local_server(authorization_prompt_message="")  # port 8080 localhost
            credentials = flow.credentials
            with open("token.pickle", 'wb') as token_file:
                pickle.dump(credentials, token_file)

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    with open("likedVideosIds.json", 'r') as ids_file:
        videos = json.load(ids_file)

    print(len(videos))
    channels = {}
    total_views = 0
    for vid_id in videos:
        request = youtube.videos().list(
            part="snippet, statistics",
            id=vid_id
        )
        response = request.execute()

        # extract
        
        try:
            channel = response["items"][0]["snippet"]["channelTitle"]
            print(channel)
            total_views += int(response["items"][0]["statistics"]["viewCount"])
            if channels.get(channel) is not None:
                channels[channel] += 1
            else:
                channels[channel] = 1
        except (IndexError, KeyError):
            print("video or channel no longer available")

    # sort dictionary
    sorted_list = sorted(channels.items(), reverse=True, key=lambda lst: lst[1])  # key=def func(lst): return lst[1]
    print(sorted_list)

    avg_views = total_views / len(videos)
    print(avg_views)


if __name__ == '__main__':
    main()