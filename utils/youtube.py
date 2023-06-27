import os
import pandas as pd
from apiclient.discovery import build
# from apiclient.errors import HttpError
import json
import streamlit as st


def get_api_info():
    service_name = 'youtube'
    version = 'v3'
    try:
        apikey = st.secrets['DEVELOPER_KEY']
    except Exception:
        with open(os.path.join(
            os.path.join(os.path.dirname(os.path.abspath(__name__))),
            'secret.json')) as f:
            apikey = json.load(f)['APIKEY']
    return service_name, version, apikey


class Youtube:
    def __init__(self, service: str, version: str, developerkey: str) -> None:
        self.app = build(service, version, developerKey=developerkey)
    
    def search(self, keyword: str, max_results: int=50) -> pd.DataFrame:
        search_response = self.app.search().list(
            q=keyword,
            part="id,snippet",
            order='viewCount',
            type='video',
            maxResults=max_results
        ).execute()

        items_id = []
        for item in search_response['items']:
            items_id.append({
                'video_id': item['id']['videoId'], 
                'channel_id': item['snippet']['channelId']
                })

        df = pd.DataFrame(items_id)
        return df
    
    def get_channel_statistics(self, 
                               channelds: list | pd.DataFrame, 
                               max_results: int=50) -> pd.DataFrame:
        
        if isinstance(channelds, pd.DataFrame):
            channles_id = channelds['channel_id'].unique().tolist()
        else:
            channles_id = channelds

        statistics_list = self.app.channels().list(
            id=','.join(channles_id),
            part='statistics',
            fields='items(id, statistics(subscriberCount))',
            maxResults=max_results
        ).execute()
        
        statistics = []
        for item in statistics_list['items']:
            if len(item['statistics']) > 0:
                statistic = {
                    'channel_id': item['id'],
                    'subscriberCount': int(item['statistics']['subscriberCount'])
                }
            else:
                statistic = {
                    'channel_id': item['id'],
                }
            statistics.append(statistic)

        df = pd.DataFrame(statistics).fillna(0.0)
        return df

    def get_extracted_videos(self, df: pd.DataFrame, subscribercount: int, 
                             mt: bool=False, lt: bool=False) -> pd.DataFrame:
        if subscribercount:
            if mt:
                extracted_df = df[df['subscriberCount'] >= subscribercount]
            else:
                extracted_df = df[df['subscriberCount'] <= subscribercount]
        return extracted_df
    
    def get_videos(self, 
                   videos: list | pd.DataFrame, 
                   max_results: int=50) -> pd.DataFrame:
        
        if isinstance(videos, pd.DataFrame):
            video_ids = videos['video_id'].tolist()
        else:
            video_ids = videos
        videos_list = self.app.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids),
            fields='items(id,snippet(title),statistics(viewCount))',
            maxResults=max_results
        ).execute()

        videos = []
        for item in videos_list['items']:
            video = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'viewCount': int(item['statistics']['viewCount'])
            }
            videos.append(video)

        df = pd.DataFrame(videos)
        return df
    
    def get(self, keyword: str, subscribercount: int, mt: bool=False, lt: bool=False, 
            max_results=50):
        # 動画検索
        search_df = self.search(keyword, max_results)
        # 統計情報取得
        statistics_df = self.get_channel_statistics(search_df)
        # マージ
        merge_df = pd.merge(left=search_df, right=statistics_df, on='channel_id')
        # フィルター
        extracted_df = self.get_extracted_videos(
            merge_df, subscribercount=subscribercount, mt=mt, lt=lt)
        
        # 動画詳細情報取得
        video_df = self.get_videos(extracted_df)
        # マージ
        merge_df = pd.merge(left=extracted_df, right=video_df, on='video_id')
        # 列順整理
        resutls = merge_df.loc[:, ['video_id', 'title', 'viewCount', 'subscriberCount', 'channel_id']]
        return resutls




if __name__ == '__main__':
    you = Youtube(*get_api_info())
    # df1 = you.search('Python 自動化', max_results=10)
    # df2 = you.get_channel_statistics(df1)
    # merge_df = pd.merge(left=df1, right=df2, on='channel_id')
    # extracted_df = you.get_extracted_videos(merge_df, subscribercount=145000, lt=True)
    # df3 = you.get_videos(extracted_df)
    # merge_df = pd.merge(left=extracted_df, right=df3, on='video_id')
    # resutls = merge_df.loc[:, ['video_id', 'title', 'viewCount', 'subscriberCount', 'channel_id']]
    print(you.get('Python 自動化', subscribercount=145000, mt=True)['subscriberCount'])

