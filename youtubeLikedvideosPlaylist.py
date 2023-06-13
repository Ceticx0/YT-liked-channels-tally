import os
import pickle
import json

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request

scopes = ["https://www.googleapis.com/auth/youtube"]


def main():
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

    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId="LL",
    )
    response = request.execute()
    print(response)
    next_page_token = response.get("nextPageToken")
    video_ids = []

    while next_page_token:
        for item in response["items"]:
            print(item["contentDetails"]["videoId"])
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if next_page_token:
            request = youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId="LL",
                    pageToken=next_page_token
            )
        response = request.execute()

    with open("likedVideosIds.json", 'w') as ids_files:
        json.dump(video_ids, ids_files)


if __name__ == "__main__":
    main()
