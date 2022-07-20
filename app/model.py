import pandas as pd
import numpy as np
import joblib
import logging

from xgboost import XGBRegressor

def create_and_pickle_model(grouped_tweets):
    logging.info('Creating and Pickling New Model')
    grouped_tweets['prev_price'] = grouped_tweets['prices'].shift(-1, axis = 0)

    grouped_tweets = grouped_tweets.dropna()

    y = grouped_tweets.prices
    X = grouped_tweets.drop(['prices', 'timestamp'], axis = 1)

    model = XGBRegressor()
    model.fit(X,y)
    joblib.dump(model , 'TwitSentModel_jlib')

    return 'success'