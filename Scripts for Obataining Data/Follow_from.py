import requests
import json

import pandas as pd
from tqdm import tqdm


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

followers_df = pd.read_csv(
    "C:/Users/lauta/OneDrive/Escritorio/twitch_followers.csv"
)


def get_followings(target, n_followers = 100, cursor = False):
    followings = []
    get = f"https://api.twitch.tv/helix/users/follows?from_id={target}&first={n_followers}"
    response =  requests.get(get, headers=headers)
    processed = json.loads(response.text)
    for following in processed["data"]:
        follower_id = following["from_id"]
        follower_username = following["from_name"]
        following_to = following["to_name"]
        following_id = following["to_id"]
        followed_at = following["followed_at"]

        follower_info = {"id":follower_id, "username":follower_username, "following_to":following_to, "following_to_id":following_id, "followed_at":followed_at}
        followings.append(follower_info)
    return followings

followings = []
for follow in tqdm(followers_df.id.unique()[65000:]):
    internal_followings = []
    get = f"https://api.twitch.tv/helix/users/follows?from_id={follow}&first=100"
    response =  requests.get(get, headers=headers)
    processed = json.loads(response.text)
    for following in processed["data"]:
        follower_id = following["from_id"]
        follower_username = following["from_name"]
        following_to = following["to_name"]
        following_id = following["to_id"]
        followed_at = following["followed_at"]

        follower_info = {"id":follower_id, "username":follower_username, "following_to":following_to, "following_to_id":following_id, "followed_at":followed_at}
        internal_followings.append(follower_info)
    total = processed["total"]
    if (len(internal_followings) < total) and processed['pagination']:
        pagination = processed["pagination"]
        cursor = pagination["cursor"]
        follower_info_extra = get_followings(follow,100, cursor)
        internal_followings.extend(follower_info_extra)
    followings.extend(internal_followings)

followings_df = pd.DataFrame(followings)
original = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_followers_plus.csv")
followings_final = original.append(followings_df)
followings_final.to_csv(
    "C:/Users/lauta/OneDrive/Escritorio/twitch_followers_plus.csv", index=False
)