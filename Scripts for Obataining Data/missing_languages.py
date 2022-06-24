from unicodedata import name
import requests
import json
from user_data import CLIENT_ID, CLIENT_SECRET
import pandas as pd
import time
from tqdm import tqdm

response = requests.post(
    f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials&scope=channel_subscriptions"
)

access = json.loads(response.text)
token = access["access_token"]
token_type = access["token_type"]

headers = {
    "Client-Id": CLIENT_ID,
    "Authorization": f"{token_type.capitalize()} {token}",
}

channels = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels_data.csv")
unknown = channels[channels["language"] == "\nPartner \n"]
unknown1 = channels[channels["language"] == "\n Partner \n"]
unknown2 = channels[channels["language"] == "Unknown"]

unknowns_df = pd.concat([unknown, unknown1, unknown2])

unknowns = list(unknowns_df["channel_name"])
languages_retrieved = []
for channel in tqdm(unknowns):
    get_language = f"https://api.twitch.tv/helix/search/channels?query={channel}"
    response = requests.get(get_language, headers=headers)
    processed = json.loads(response.text)

    data = processed["data"]
    for i in range(0, len(data)):
        try:
            name = data[i]["display_name"]
            if name != channel:
                continue
            language = data[i]["broadcaster_language"]
        except IndexError:
            name = channel
            language = "Not Found"
        channel_info = {"channel_name": name, "language": language}
        languages_retrieved.append(channel_info)

languages_df = pd.DataFrame(languages_retrieved)
languages_df.to_csv(
    "C:/Users/lauta/OneDrive/Escritorio/twitch_languages_missing.csv", index=False
)
