import tweepy
import json 
import pymongo
import pprint
import kmeans
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
from distance import jaccard as jacc
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import operator 

def tweepySetup():
	#keys are in a file for saftey reasons
	file1 = open('/Users/alextaylor/Desktop/twitter_codes','r') 
	twitterCodes = file1.readlines()

	api_key = twitterCodes(0)
	secret_key = twitterCodes(1)

	access_token = twitterCodes(2)
	access_token_secret = twitterCodes(3)


	auth = tweepy.OAuthHandler(api_key, secret_key)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth,parser=tweepy.parsers.JSONParser())

def basicSearch():
	#only run these for getting data from twitter 

	buffer = api.search(q = "Lunch", lang = "en", rpp = 5,tweet_mode='extended')

def mongoDBSetup:
	#mongo db setup stuff 
	from pymongo import MongoClient

	#first off link it to the db
	client = MongoClient('localhost',27017)

	database = client['WebSciTwitter']

	collection = database.testCollection

	database.enablefreemonitoring

	database.list_collection_names()

def twitterStreamSetuo():
	#set up for the stream 

	collection = database.rawTwitterData
	rawTwitterData = database.rawTwitterData
	retweet = False
	retweetName = ""

	collections = []
	hashtags = []

	class MyStreamListener(tweepy.StreamListener):

	    def on_status(self, status):
	        
	        retweet = False

	        #print(status._json["lang"])
	        retweetName = ' '
	        hashes1 = status._json['entities']['hashtags']
	        hashtags = []
	        for item in hashes1:
	            hashtags.append(item['text'])
	        
	        retweetData = []
	        if status._json["text"][:2] == "RT":
	            
	            retweetName = status._json['text'].split()[1][1:-1]
	            #print(retweetName)
	            retweet = True
	            #print(status._json)
	            hashes = status._json['retweeted_status']['entities']['hashtags']
	            for item in hashes:
	                hashtags.append(item['text'])
	            
	        
	       
	        if status._json["lang"] == "en":
	            #save the text for now 
	            dictToAdd = {"text":status._json["text"],"jac":0,"username":status._json["user"]["name"],"reply_to":status._json["in_reply_to_screen_name"],"mentions":status._json["entities"]["user_mentions"],'retweeted':retweet,'rtName':retweetName, 'hash': hashtags}
	            rawTwitterData.insert_one(dictToAdd)
	            #print(retweet)
	            
	        
	myStreamListener = MyStreamListener()
	myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener(),parser=tweepy.parsers.JSONParser(), lang = "en", rpp = 5,tweet_mode='extended')

def startStream():
	#tweepy stream for filtered 
	myStream.filter(track=['game'])   
	
	#generates a value for each tweet based on the jaccard metric and pass it to the db

def jaccardSetUp():

	curse = rawTwitterData.find()

	count = 0
	checker = ""
	jac = 0

	df = pd.DataFrame({"1"})

	for item in curse:
	    if count == 0:
	        checker = item['text']
	    
	    
	    jac = jacc(item['text'],checker)
	    #print(jac)
	    
	    dictToAdd = {count:jac}
	    
	    #add obj to the data frame
	    df2 = pd.DataFrame.from_dict(dictToAdd,orient = "index")
	    #print(df2)
	    df = df.append(df2)
	    #print(df)
	    #print(df2)
	    
	    database.rawTwitterData.update({"_id": item["_id"]},{"text":item["text"],"jac":jac,"username":item["username"],"reply_to":item["reply_to"],"mentions":item["mentions"],'retweeted':item['retweeted'],'rtName':item['rtName'], 'hash': item['hash']})
	    
	    count +=1

def kMeans():
	#info now in a data frame so now 
	x = df.iloc[:,[0]].values

	predK = 0

	kMeans = KMeans(n_clusters=5)

	predK  = kMeans.fit_predict(x)

	#print(predK)

	num0 = (predK==0).sum()
	num1 = (predK==1).sum()
	num2 = (predK==2).sum()
	num3 = (predK==3).sum()
	num4 = (predK==4).sum()
	#num5 = (predK==5).sum()

	print(num0,num1,num2,num3,num4)

	count = 0
	curse = rawTwitterData.find()
	for item in curse:
	    #step throught and fire back to the db the index of each one 
	    database.rawTwitterData.update({"_id": item["_id"]},{"text":item["text"],"jac":item['jac'],"group":str(predK[count]),"username":item["username"],"reply_to":item["reply_to"],"mentions":item["mentions"],'retweeted':item['retweeted'],'rtName':item['rtName'], 'hash': item['hash']})
	    count +=1
 
def mentionFreq():
	#for each user: mentions
	mentions = {}
	mentionsCount = {}
	currentDict = {}

	curse = rawTwitterData.find()

	for item in curse:
	    #so check for mentions
	    #if item['group'] is '4':
	        if(item["mentions"]):
	            #so there are mentions- set the current dict
	            currentDict = mentions.get(item['username'])
	            if currentDict == None:
	                currentDict = {'dumb': 1}
	            for mName in item['mentions']:
	               # print(currentDict)
	                cName = mName['name']
	                #if key in dict
	                if cName in currentDict:
	                    #print(currentDict)
	                    #print(mName)
	                    currentDict[mName['name']] += 1
	                    mentionsCount[mName['name']] += 1

	                else:
	                    #print('adding new')
	                    currentDict[cName] = 1
	                    mentionsCount[cName] = 1
	            #del currentDict['dumb']

	            mentions.update( {item['username']: currentDict})
	print(len(mentions))

	#user i -> userj, freq; userk, freq

def retweets():
	#retweets 
	#for each user: 

	retweets = {}
	currentDict = {}

	curse = rawTwitterData.find()

	for item in curse:
	    #so check for mentions
	    #print(item["retweeted"])

	    #if item['group'] is '':
	        if(item["retweeted"]):
	            #there is a retweet


	            #so there are mentions- set the current dict
	            currentDict = retweets.get(item['username'])
	            if currentDict == None:
	                currentDict = {'dumb': 1}

	            cName = item['rtName']

	            # print(currentDict)

	            if cName in currentDict:
	                #print('updating')
	                currentDict[cName] += 1
	            else:
	                #print('adding new')
	                currentDict[cName] = 1
	            #del currentDict['dumb']
	            retweets.update( {item['username']: currentDict})
	print(len(retweets))

def hashtags():
	#for hashtag data save - dict with the hashtags {hashtag:amount}
	hashtags = {}
	currentDict = {}

	curse = rawTwitterData.find()


	for item in curse:
	    if(item['hash']):
	        #theres is a hashtag
	        #if item['group'] is '0':
	            for hashtag in item['hash']:
	                #print(hashtag)
	                #print(len(hashtag))
	                cName = hashtag
	                if currentDict == None:
	                    currentDict = {'dumb': 1}
	                if cName in currentDict:
	                    currentDict[cName] += 1
	                else:
	                    currentDict[cName] = 1

	                #del currentDict['dumb']
	            hashtags.update( currentDict)
	print(len(hashtags))

def ties():
	#ties and triads 
	#a tie is when two users connect so total num of users, a tie is created when retweet or replies 
	#loop over retweets and use a list [user:user] to record links 

	ties = []

	#retweets- 
	for item in retweets.keys():
	    #print(item)
	    #print(retweets[item])
	    for link in retweets[item]:
	        #print(link)
	        #tie between item,link
	        if (item,link) not in ties:
	            ties.append((item,link))            

	#mentions 
	for item in mentions.keys():
	    #print(item)
	    #print(retweets[item])  
	    for link in mentions[item]:
	        #print(link)
	        #tie between item,link
	        if (item,link) not in ties:
	            ties.append((item,link))

	print(len(ties))

def triads():
	#triads - part 2 
	triads = []
	holder = []

	for item in ties:
	    #create a list of each item be
	    begin = item[0]
	    end = item[1]
	    
	    #create a list of pairs (begin,x)
	    for item in ties:
	        if(item is not  [begin,end]):
	            if(item[0] is begin):
	                holder.append(item)
	    #so does holder have (x,end)
	    for item in holder:
	        if item[1] is end:
	            #print('Triad')
	            #triad 
	            cTriad = [begin,item[0],end]
	            if cTriad not in triads:
	                triads.append(cTriad)
	    #print(len(triads))
	    
	print(len(triads))

#This def was used to get the max value out of a dict
def getValues():
	value = max(totMen.items(), key=operator.itemgetter(1))[0]

	print(value)
	print(totMen[value])

def importantUsers():
	#most important users 
	users = {}
	curse = rawTwitterData.find()

	for item in curse:
	    #if item['group'] is '4':
	        if item["username"] in users:
	            users[item['username']] +=1
	        else:
	            users[item['username']] =1
	print(users.values())
	print(max(users.items(), key = operator.itemgetter(1))[0])

def totalMentions():
	totMen = {}
	for item in mentions.keys():
	    for key in mentions[item].keys():
	        #print(mentions[item][key])
	        if key in totMen:
	            totMen[key] += mentions[item][key]
	        else:
	            totMen[key] = mentions[item][key]
	totMen['dumb'] = 0

	value = max(totMen.items(), key=operator.itemgetter(1))[0]

	print(value)
	print(totMen[value])





