import requests
import json
from user_data import CLIENT_ID, CLIENT_SECRET
import pandas as pd
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

channels = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels.csv")
followers = []

for channel in tqdm(channels.id.unique()):
    get_followers = (
        f"https://api.twitch.tv/helix/users/follows?to_id={channel}&first=100"
    )

    response = requests.get(get_followers, headers=headers)
    processed = json.loads(response.text)

    total_followers = processed["total"]
    channels.loc[channels["id"] == channel, ["total_followers"]] = total_followers

    for follower in processed["data"]:
        follower_id = follower["from_id"]
        follower_username = follower["from_name"]
        following_to = follower["to_name"]
        following_id = follower["to_id"]
        followed_at = follower["followed_at"]

        follower_info = {
            "id": follower_id,
            "username": follower_username,
            "following_to": following_to,
            "following_to_id": following_id,
            "followed_at": followed_at,
        }
        followers.append(follower_info)

followers_df = pd.DataFrame(followers)
followers_df.to_csv(
    "C:/Users/lauta/OneDrive/Escritorio/twitch_followers.csv", index=False
)
