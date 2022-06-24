import requests
import json
import pandas as pd

CLIENT_ID = "jz41id5h1skmo6o60l6wunvcyzn8yj"
CLIENT_SECRET = "a7fbeuwbc724d9iw4uw6pnjsmdr1g9"

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

channels = []

get_channels = "https://api.twitch.tv/helix/streams?first=100"

response = requests.get(get_channels, headers=headers)
processed = json.loads(response.text)

for j in processed["data"]:
    id = j["user_id"]
    name = j["user_name"]
    game_name = j["game_name"]
    game_id = j["game_id"]
    title = j["title"]
    viewers = j["viewer_count"]
    language = j["language"]
    started = j["started_at"]

    channel = {
        "id": id,
        "name": name,
        "game": game_name,
        "game_id": game_id,
        "title": title,
        "viewers": viewers,
        "language": language,
        "started": started,
    }
    channels.append(channel)

channels_df = pd.DataFrame(channels)

before_df = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels.csv")
final = before_df.append(channels_df)
final.drop_duplicates(["name", "game"], keep="last", inplace=True)
final.to_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels.csv", index=False)

checking = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels.csv")
checking.head()
