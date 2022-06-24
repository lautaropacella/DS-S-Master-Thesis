import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

def get_general(channel):
    url = f'https://twitchtracker.com/{channel}'

    response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})

    while response.status_code == 503:
        time.sleep(10)
        response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})

    if response.status_code == 404:
        return
   
    elif response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_checker = soup.find_all('div', class_ = 'g-x-wrapper')
        if not data_checker:
            return
        divs = soup.find_all('div',class_='g-x-s-block')


        total_hours =  divs[0].find('div', class_ = 'to-number').text
        record_viewers =  divs[1].find('div', class_ = 'to-number').text
        total_followers =  divs[2].find('div', class_ = 'to-number').text
        total_views =  divs[3].find('div', class_ = 'to-number').text

        if len(divs) > 4:
            try:
                active_subs =  divs[4].find('div', class_ = 'to-number').text
            except AttributeError:
                active_subs = np.nan
            try:
                paid_subs = divs[5].find('div', class_ = 'to-number').text
            except AttributeError:
                 paid_subs = np.nan
            try:
                gifted_subs =  divs[6].find('div', class_ = 'to-number').text
            except AttributeError:
                gifted_subs = np.nan
            try:
                record_subs = divs[7].find('div', class_ = 'to-number').text
            except AttributeError:
                record_subs = np.nan
        else:
            active_subs = np.nan
            paid_subs = np.nan
            gifted_subs = np.nan
            record_subs = np.nan

        streamer_col = soup.find('div', class_= 'col-md-3 col-sm-4')
        attrs = streamer_col.find_all('span')
        language = attrs[5].text
        created =  attrs[6].text
        data = {'total_hours': total_hours, 'total_views': total_views, 'total_followers':total_followers, 'record_viewers': record_viewers,
        'active_subs': active_subs, 'paid_subs':paid_subs, 'gifted_subs':gifted_subs, 'record_subs':record_subs, 'language': language, 'created':created}
        
        return data

def get_games(channel):
    url = f'https://twitchtracker.com/{channel}/games'
    response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})
    
    while response.status_code == 503:
        time.sleep(10)
        response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})

    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all('tr')
    data = {'most_played' : rows[1].find('a').text}

    for i in range(2, 6):
        try:
            data.update({f'{i}_most_played': rows[i].find('a').text})
        except IndexError:
             data.update({f'{i}_most_played': np.nan})
    return data


def get_stats(channel):
    url = f'https://twitchtracker.com/{channel}/statistics'
    response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})
    
    while response.status_code == 503:
        time.sleep(10)
        response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'})

    soup = BeautifulSoup(response.text, 'html.parser')

    controls = soup.find('div', class_='pg-controls')

    controls_data = controls.find_all('span')

    hours_streamed = controls_data[2].text
    hours_watched = controls_data[3].text
    average_viewers = controls_data[4].text
    active_days = controls_data[6].text

    tables = soup.find_all('table', class_= 'table table-bordered table-condensed')
    hours_data = tables[1].find_all('span')
    average_hours = hours_data[0].text
    active_days_per_week = hours_data[2].text

    table_games = tables[2].find_all('span')
    average_games = table_games[2].text

    data = {
            'hours_streamed' : hours_streamed,
            'hours_watched' : hours_watched,
            'average_viewers' : average_viewers,
            'active_days' : active_days,
            'average_hours' : average_hours,
            'active_days_per_week': active_days_per_week,
            'average_games': average_games
            }
    return data


df = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_followers_partners.csv")

channels = []

for channel_name in tqdm(df.following_to.unique()[9500:]):
    print(channel_name)
    
    channel_data = get_general(f'{channel_name}')
    if channel_data:
        time.sleep(3)
        channel_stats = get_stats(f'{channel_name}')
        time.sleep(3)
        channel_games = get_games(f'{channel_name}')

        channel = {'channel_name':channel_name}

        scraped_data = [channel_data, channel_stats, channel_games]
        for data in scraped_data:
            channel.update(data)
        channels.append(channel)
        time.sleep(3)
    else:
        continue

channels_data_df = pd.DataFrame(channels)

original = pd.read_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels_data.csv")
channels_final = original.append(channels_data_df)
channels_final.to_csv("C:/Users/lauta/OneDrive/Escritorio/twitch_channels_data.csv", index=False)

channels_final

original