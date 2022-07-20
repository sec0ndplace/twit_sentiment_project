import requests
import os
import json
import pandas as pd
from pycoingecko import CoinGeckoAPI
import csv
import datetime
import logging


from textblob import TextBlob
from dotenv import load_dotenv, find_dotenv
from sentiment import *

#contains functions to grab data from twitter api and grade it by sentiment

def create_url(keyword, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/recent" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date.isoformat() + 'Z',
                    'end_time': end_date.isoformat() + 'Z',
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    #'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)

def create_headers(bearer_token):
    logging.info('Creating headers from .env file')
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        logging.info('Connection failed! (Status code != 200')
        raise Exception(response.status_code, response.text)
    return response.json()

def get_data_from_twitter():
    load_dotenv() #my env is untracked (has my tokens)
    token = os.environ.get("bearer_token")

#times are in ISO-8601
    headers = create_headers(token)
    end_time = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15)
    start_time = end_time - datetime.timedelta(days = 1)
    max_results = 24 #10 is minimum
    keyword = "#eth lang:en"


    cg = CoinGeckoAPI()
    #cg.get_coins_list()
    logging.info('Getting yesterday\'s price history on ETH from coingecko')
    past_prices = pd.DataFrame(cg.get_coin_market_chart_by_id(id='ethereum', vs_currency='usd', days=2))

    for col in past_prices:
        timestamps, var = zip(*past_prices[col])
        past_prices['timestamp'] = timestamps
        past_prices[col] = var

    #timestamps, ms_garbage = divmod(timestamps, 1000)
    timestamps = [datetime.datetime.utcfromtimestamp(divmod(timestamp, 1000)[0]) for timestamp in timestamps]

    past_prices['timestamp'] = timestamps

    past_prices.head()

    # times to grab data - choose intervals to grab tweets from
    #time_list = [end_time - datetime.timedelta(seconds = 30) - datetime.timedelta(hours=x) for x in range(0, 12*1)]

    time_list = past_prices['timestamp']
    #time_list = past_prices[0:10]

    #parameters - how many tweets from each ?
    max_results = 20
    keyword = "#eth lang:en"

    dataset = pd.DataFrame()

    logging.info('Fetching tweets for provided times')

    for time in time_list:
        start = time - datetime.timedelta(hours = 6)
        end = time
        url, params = create_url(keyword, start, end,max_results)
        json = connect_to_endpoint(url, headers, params)
        tweets = pd.DataFrame(json['data'])
        tweets['timestamp'] = time
        dataset = dataset.append(tweets, ignore_index=True)   
        del tweets

    logging.info('Assigning Sentiment Values...')
    sentiment_analysis(dataset)
    grouped_tweets = dataset.groupby('timestamp').mean()
    grouped_tweets = pd.merge(grouped_tweets, past_prices[['timestamp', 'prices', 'total_volumes']], how="inner", on="timestamp")

    logging.info('Writing csv')
    grouped_tweets.to_csv('./groupedtweets.csv', mode='a')
    return(grouped_tweets)