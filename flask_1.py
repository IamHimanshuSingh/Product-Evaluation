from flask import Flask,render_template,request
from os import sys
import tweepy
import re
from textblob import TextBlob
import geocoder
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map,icons
import csv



#=========================================================================
consumer_key = 'Your consumer key'
consumer_secret = 'Your consumer secret'
access_token = 'Your access token'
access_token_secret = 'Your access token secret'

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
api.wait_on_rate_limit = True
api.wait_on_rate_limit_notify = True

#=================================================================================



#=============================Tweet Collection======================================
def collect_tweets(place,query):
    cnt=0
    try:
        print("================================start=========================================")
        for i in range(1):
            avg=0
            g = geocoder.google(place)
            g_string=str(g.lat)+","+str(g.lng)+","+"100mi" 
            saveFile = open('dat2.csv','a')
            for tweet in tweepy.Cursor(api.search,q=query,lang='en',geocode=g_string).items(50):
                cnt=cnt+1                
                analysis = TextBlob(tweet.text)
                avg=avg + analysis.sentiment.polarity
                saveFile.write(str(tweet.created_at) + ",")
                saveThis = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(u2026)|(https)", " ", tweet.text).split())
                saveFile.write(saveThis + "," + str(analysis.sentiment.polarity ))
                saveFile.write('\n')        
                print(analysis.sentiment.polarity)        
    
    
            print("\n===========================end=========================================")
            saveFile1 = open('dat3.csv','a')
            saveFile1.write(query + "," + place + "," + str(g.lat) + "," + str(g.lng) + "," + str(avg/50))
            saveFile1.write('\n')
            
        saveFile1.close()
        print(cnt)
    except:
        print("Oops!",sys.exc_info()[0],"occured.")
        #cnt=0;
        
    return cnt

#=========================User Interface======================

app = Flask(__name__,static_folder='C:\\Users\\Himanshu\\Desktop\\sdl\\sentiment_analysis-master')

@app.route('/')
def dir1():
    return render_template("profile.html")

GoogleMaps(app)

@app.route('/map' , methods = ['POST'])
def mapview():
        places = request.form['place']
        queries = request.form['query']
        count = collect_tweets(places,queries)
        locs={'color':[],'lats':[],'lons':[]}
        if(count > 0):
            filename = 'dat3.csv'
            #latitude, longitude = [], []   
            #k=0
            with open(filename) as f:
                reader = csv.reader(f)
                for row in reader:
                    if(row[0]==queries):
                        #k=k+1
                        locs['lats'].append(float(row[2]))
                        locs['lons'].append(float(row[3]))
                        if(float(row[4])>0.1):
                            locs['color'].append(icons.dots.green)
                        elif(float(row[4])>-0.01 and float(row[4])<0.1):
                            locs['color'].append(icons.dots.yellow)
                        else:
                            locs['color'].append(icons.dots.red)
                        
            tup=list(zip(locs['color'],locs['lats'],locs['lons']))        
            print(tup)            
            trdmap = Map(
                identifier="trdmap",
                lat=locs['lats'][0],
                lng=locs['lons'][0],
                #[[i for i in d[x]] for x in d.keys()]
                markers=[{'icon':itr[0],'lat':itr[1],'lng':itr[2]} for itr in tup],
                zoom=4
            )
                #print(sys.exc_info()[0])        
            return render_template('example.html', trdmap=trdmap)    
        else:
            return render_template("error.html")
        


if __name__ == '__main__':
    app.run()

#===================================End===========================================
