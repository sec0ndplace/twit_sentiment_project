"""
db.py

"""
from sqlalchemy import create_engine
import pandas as pd
import logging
import dotenv
import os

class PG_Data():
    def __init__(self):
        dotenv.load_dotenv()
        self.pg_user = os.environ.get('PG_USER')
        self.pg_pass = os.environ.get('PG_PASS')
        self.pg_host = os.environ.get('PG_HOST')
        self.pg_port = os.environ.get('PG_PORT')
        self.pg_db = os.environ.get('PG_DB')

    def __get_engine(self):
        try:
            engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{db}'.format(user = self.pg_user,
                                                                                  password = self.pg_pass,
                                                                                  host = self.pg_host,
                                                                                  port = self.pg_port,
                                                                                  db = self.pg_db))
            return engine

        except Exception as err:
            logging.error('Unable to connect to postgres', err)
            print('Unable to connect to make engine connect to Postgres', err)

        
    def __close_engine(self, engine):
        if engine != None:
            logging.debug('disposing engine')
            engine.dispose()

    def get_all_data(self):
        engine = self.__get_engine()

        # Put a limit here because it is slow when loading to browser
        try:
            logging.info('attempting to get all airlines data')
            query = """SELECT * FROM tweets;"""
            all_tweets = pd.read_sql(query, engine)
            
        except Exception as err:
            logging.error('Unable to get data from {db}'.format(db = self.pg_db), err)
            print('Unable to get data from {db}'.format(db = self.pg_db), err)
            all_tweets = None

        self.__close_engine(engine)

        return all_tweets

    def get_one_data(self):
        engine = self.__get_engine()

        # Put a limit here because it is slow when loading to browser
        try:
            logging.info('attempting to get all airlines data')
            query = """SELECT * FROM tweets LIMIT 1;"""
            tweet = pd.read_sql(query, engine)
            
        except Exception as err:
            logging.error('Unable to get data from {db}'.format(db = self.pg_db), err)
            print('Unable to get data from {db}'.format(db = self.pg_db), err)
            tweet = None

        self.__close_engine(engine)

        return tweet
    
    def add_data(self, tweets):
        engine = self.__get_engine()
        try:
            logging.info('Creating new tweets table')
            tweets.to_sql('tweets', engine, if_exists='append')
            success = "success"

        except Exception as err:
            logging.error('Unable to create tweets table')
            print('Unable to create tweets table')
            success = "failure"
    
        return success