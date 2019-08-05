import requests
import pandas as pd
import datetime
import numpy as np
import json

def refresh_stats():
    heroes = []


    headers = {
        'authority': 'overwatchleague.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': '__cfduid=db205ea20f0bdcc1822b5c4b296da02621545060876; optimizelyEndUserId=oeu1545063133530r0.5770034645398332; _ga=GA1.2.1224397857.1545063135; _cb_ls=1; _cb=DzcjmGCMtiS2CKqV2j; _fbp=fb.1.1550479138474.193312463; locale=en_US; session=61YlWJtbT7TcXF9l4DZ2Eg.qQB16Yw06F_3zHpJ5BVeqtm-f7lXEYfbwM5RD70EN4QH1ngbZ-QazR4SNMCpe3uj_oPQ2x-tyy3IGF96KWkXcw.1553165019662.86400000.pV5UK_VY3AdBB2t9Lce6ZFn42iS23gmekGvvIDRuPVw; _gid=GA1.2.178122901.1553165023; _gat_UA-50249600-51=1; showSpoilers=true; _sctr=1|1553097600000; _scid=8b8121fd-ece3-4598-9f5f-ce393e6ae7df; _chartbeat2=.1545063137579.1553165026254.0000000000000001.CLQM1kkhiGxDMDv1ACL8kf212qTp.1; _cb_svref=null',
    }
    player_stats = requests.get(
        'https://api.overwatchleague.com/player?season=2019&expand=stats',headers=headers, timeout=10).json()

    def parse_stats(stats):
        return {item['name']: item['value'] for item in stats}

    for player in player_stats:
        if player['stats'] is None:
            continue
        print(player['stats'])
        base_info = {'hero_name': 'overall',
                    'player_name': player['name'], 'team_name': player['teams'][0]['team']['abbreviatedName']}
        heroes.append(dict(**base_info, **parse_stats(player['stats']['stats'])))
        for hero in player['stats']['heroes']:
            base_info['hero_name'] = hero['name']
            heroes.append(dict(**base_info, **parse_stats(hero['stats'])))
    df = pd.DataFrame(heroes).fillna(0).set_index(
        ['hero_name', 'player_name', 'team_name'])
    current = pd.read_csv('data/heroes.csv').set_index(
        ['hero_name', 'player_name', 'team_name'])
    df.to_csv('data/heroes.csv')
    if current.shape != df.shape or not all([all(l) for l in np.isclose(df, current)]):
        df.to_csv("history/" + datetime.datetime.now().strftime("%Y%m%d%H%M") + '.csv')
    df = pd.DataFrame(heroes, columns=[
        'hero_name', 'player_name', 'team_name',
        'time_played_total',
        'damage_avg_per_1m',
        'healing_avg_per_1m',
        'eliminations_avg_per_1m',
        'deaths_avg_per_1m',
        'accuracy_avg',
        'damage_taken_avg_per_1m',
        'damage_blocked_avg_per_1m']).fillna(0)
    with open('data/data.json', 'w') as outfile:
        json.dump({"data": df.round(2).values.tolist()},
                  outfile, ensure_ascii=False)
        return True
    

if __name__ == '__main__':
    refresh_stats()
