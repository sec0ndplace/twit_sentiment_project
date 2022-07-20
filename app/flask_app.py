from operator import index
import requests
import os
import json
import pandas as pd
import csv
import datetime
import joblib
from pycoingecko import CoinGeckoAPI
from flask import Flask, request
from textblob import TextBlob
from dotenv import load_dotenv, find_dotenv
from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger

from twitter import *
from sentiment import *
from model import *
from db import *

app = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

pg_data = PG_Data()

@app.route('/health-check')
def health_check():
    logging.info('Health Check Requested')
    return 'OK'

# get's previous day's price info for Ethereum, and adds the data to postgres table
@app.route('/get_data', methods = ['GET'])
def get_data():
    logging.info('Get and Import New Data From Twitter')
    new_data = get_data_from_twitter()
    pg_data.add_data(new_data)
    return new_data.to_json()

@app.route('/get_all_data', methods = ['GET'])
def get_all_data():
    logging.info('Get All Data Stored in Postgres DB')
    all_data = pg_data.get_all_data()
    return all_data.to_json()

@app.route('/get_sample_json', methods = ['GET'])
def get_sample_json():
    logging.info('Get a sample JSON to use for prediction purposes')
    tweet = pg_data.get_one_data()
    tweet['prev_price'] = tweet['prices']
    tweet = tweet.drop(['prices', 'timestamp'], axis = 1)
    return tweet.to_json()

@app.route('/create_model', methods = ['POST'])
def create_model():
    return create_and_pickle_model(pg_data.get_all_data())

#predicts eth price for next hour, to get a usable json use the POST method get_sample_json
@app.route('/predict_eth_hourly', methods = ['POST'])
def predict():
    if os.path.exists('TwitSentModel_jlib') == 0:
        create_model()
    predictme = pd.read_json(request.data)
    predict_eth_model = joblib.load('./TwitSentModel_jlib')
    prediction= predict_eth_model.predict(predictme)
    print(prediction)
    return str(prediction[0])
    


scheduler.add_job(func = get_data, trigger = CronTrigger.from_crontab('5 5 * * *'), name = 'get data', id = '1')

app.run(host= '0.0.0.0', port=8000, debug = True)