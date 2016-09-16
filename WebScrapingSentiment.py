# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 18:23:51 2016

@author: Stephane
"""
### Imports and constants




''' 
store your top secret Twitterkeys into a file TwitterKeys.py in the cwd
consumer_key = " "
consumer_secret = ""

access_key = ""
access_secret = ""
'''
from TwitterKeys import *
import os
#from bs4 import BeautifulSoup
import requests
import datetime, time
import pandas as pd
import numpy as np
#import re
#import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#from nltk import tokenize
import tweepy
from PIL import Image
from StringIO import StringIO
from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
import json

# constant strings used
IMDB_URL = "http://m.imdb.com/feature/bornondate"
IMDB_URL_BASE = "http://m.imdb.com/feature/bornondate_json?today="
NUMBEROFTWEETS = 100
NUMBEROFCELEBS= 10
WORKINGDIRECTORY = "d:/dev/gitrepo/WebScrapingSentiment"

# set your working directory
os.chdir(WORKINGDIRECTORY)
### Functions

def jsonLoad(baseURL):
    '''
    Input is the base IMDB URL for JSON, output is the JSON object
    Examine the normal URL in Chrome development tools > network and notice
    that a second call is made to a URL returning the required list in 
    JSON format. This is the quickest way to the list of celebs born
    on the specified date.
    '''
    print "Scraping data from IMDB website..."    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    IMDB_JSON = IMDB_URL_BASE+today
    jsonLoad = requests.get(IMDB_JSON).json()
    return jsonLoad


def buildCelebTableFromJson(load, numberOfRows=10):
    '''
    Input is the json load and #of celebs, output is a dataframe with celebs
    From the raw json load, extract the celebs, their profession, famous work
    and a picture that is stored as a PIL image.
    '''
    table = []    
    print "Building celeb table.."
    for celeb in load["list"][0:NUMBEROFCELEBS]:
        row = []
        row.append(celeb["title"])
        row.append(celeb["detail"].split(',')[0])
        row.append(celeb["detail"].split(',')[1].strip().replace('"', ''))
        row.append(Image.open(StringIO(requests.get(celeb["img"]["url"]).content)))
        table.append(row)

    df = pd.DataFrame(table, columns=('celeb', 'Profession', 'BestWork', 'Image') )     
    return df

"""
# this section is for future reference
# we use PhantomJS because the web page is executing jquery which takes time
# with an implicit wait we give the web server time to build the final page    

def getSoup(baseURL):
    '''
    Input is the base IMDB URL, output is the soup object
    Because the base URL is using jquery, a normal request.get would not get
    all the data, as the main list is still loading.
    To force an implicit wait, a PhantomJS driver is used (to be installed
    in your main PATH on your development machine) and then a call to the 
    selenium package is done.
    Parsing the soup object is significantly more complex then using the 
    direct JSON result. Therefore we choose for the direct JSON approach.
    '''
    driver = webdriver.PhantomJS()
    driver.implicitly_wait(10)
    driver.get(baseURL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()
    return soup

def buildCelebTableFromSoup(load, numberOfRows):
    df = load.find("section")
        
def printImagesCelebs(images):
    '''
    Input are images, output are pictures sent to your PC image application.
    '''    
    for img in images:    
        img.show()
"""

def tweetsFromCeleb(celeb):
    '''
    Input is the name of the celeb as str, output is the list of tweets
    100 tweets are returned. Only TEXT elements are returned as a list.
    '''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    #Put your search term
    searchquery = celeb

    users =tweepy.Cursor(api.search,q=searchquery).items()
    count = 0
    errorCount=0
    texts=[]
    
    while True:
        try:
            user = next(users)
            count += 1
            #use count-break to define number of tweets
            if (count>NUMBEROFTWEETS):
                break
        except tweepy.TweepError:
            #catches TweepError when rate limiting occurs, sleeps, then restarts.
            #See https://blog.twitter.com/2008/what-does-rate-limit-exceeded-mean-updated 
            #for explanation.
            print "Twitter Rate limit occured.Sleeping....or press CTRL-C to interrupt"
            time.sleep(60*16)
            user = next(users)
        except StopIteration:
            break
        try:
            texts.append(user._json["text"])
        except UnicodeEncodeError:
            errorCount += 1
            print "UnicodeEncodeError,errorCount ="+str(errorCount)
    
    print "\t"+celeb+" completed, errorCount ="+str(errorCount)+" total tweets="+str(count)

    return texts

def allTweets(celebs):
    '''
    Input is the list of celebs, output a dict with all their tweets
    Simply go through the list of celebs and get NUMBEROFTWEETS for each
    '''
    result = {}
    print "Getting tweets from celebs (this may take some time)..."
    for c in celebs:
        result[c] = tweetsFromCeleb(c)
    return result
    

def sentimentAnalysis(celebTweets):
    '''
    Input is a list of tweets (strings), output is the estimated sentiment
    NLTK kit is used. See http://www.nltk.org/howto/sentiment.html for 
    examples.
    All tweets of 1 celeb should be presented together. For each sentence
    the code calculates a compound sentiment (also neg/neu/pos are available)
    Then the mean of the compounds is returned.
    '''
    sid = SentimentIntensityAnalyzer()
    compound = []
    for sentence in celebTweets:
         #print sentence
         ss = sid.polarity_scores(sentence)
         compound.append(ss["compound"]) 

    return np.mean(compound)

def celebSentiments(tweetTexts):
    '''
    Input: all tweet texts, output: dictonary celeb:sentiment
    '''
    print "Getting the sentiment of the tweets ..."
    sentDict = {}
    for celeb in tweetTexts:
        sentiment = round(sentimentAnalysis(tweetTexts[celeb]),3)
        print "\t"+celeb+"\t "+sentiment
        sentDict[celeb] = sentiment
    return sentDict

def printTable(celebTable):
    print '''
    Celebrity overview, born today
    Sentiment score from -1 (negative) to 0 (neutral) to 1 (positive)
    '''
    for row in celebTable.iterrows():    
        print "Name of the celebrity \t\t: ", row[1]["celeb"]
        #uncomment below line, this will call up your PC image viewer
        #print "Celebrity Image \t\t: "#, row[1]["Image"].show()
        print "Profession \t\t\t: ", row[1]["Profession"]
        print "Best Work \t\t\t: ", row[1]["BestWork"]
        print "Overall Twitter Sentiment\t: ", row[1]["Sentiment"]
        print 
 
### the real stuff, do the work     
     
if __name__ == '__main__':
    # scrape the web
    rawJSON = jsonLoad(IMDB_URL_BASE)
    
    # get celeb info out of the raw material
    celebTable = buildCelebTableFromJson(rawJSON)
    
    # get latest Twitter tweets about the celebs in a dict
    tweetTexts= allTweets(celebTable["celeb"])

    # get sentiment and merge with celeb table
    d = celebSentiments(tweetTexts) 
    celebTable["Sentiment"]= celebTable["celeb"].map(d)

    # produce the final output    
    printTable(celebTable)



