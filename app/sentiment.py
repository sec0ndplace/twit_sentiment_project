from sklearn import preprocessing
from textblob import TextBlob
import pandas as pd
import preprocessor as prepro


def sentiment_analysis(tweet):
    def getSubjectivity(text):
        #preprocessor cleans out urls, @s, emojis
        return TextBlob(prepro.clean(text)).sentiment.subjectivity

    #Create a function to get the polarity
    def getPolarity(text):
        return TextBlob(prepro.clean(text)).sentiment.polarity

    #Create two new columns 'Subjectivity' & 'Polarity'
    tweet['TextBlob_Subjectivity'] = tweet['text'].apply(getSubjectivity)
    tweet ['TextBlob_Polarity'] = tweet['text'].apply(getPolarity)
    def getAnalysis(score):
        if score < 0:
            return 'Negative'
        elif score == 0:
            return 'Neutral'
        else:
            return 'Positive'
    tweet ['TextBlob_Analysis'] = tweet  ['TextBlob_Polarity'].apply(getAnalysis )
    return tweet