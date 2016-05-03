#!/usr/bin/env python

import requests
import time
import redis
import urllib3
from pymongo import MongoClient, GEOSPHERE
####################
# Info We Care About Retreiving from this fetch
# latitude, longitude, complaint_type, created_date
#
####################

# this is login info for our mongodb instance. We only use mongodb to lookup neighborhood based on lat,lon values
db_password = "macgregor0dewar"
db_user = "storyteller"
uri = 'mongodb://{user}:{pw}@ds015690.mlab.com:15690/storytelling'.format(user=db_user, pw=db_password)

client=MongoClient(uri)
db=client.get_database("storytelling") #our db name
coll_name = "neighborhoodsDOCP" #our collection
coll=db.get_collection(coll_name) #getting results from our collection
coll.create_index([("coordinates", GEOSPHERE)]) #index from geosphere


def get_historical_complaints():
  polling = True
  offset=0
  counter=0 # to see how many things we've inputted into redis
  offset_iterator=0 # how many offsets we have done so we can see progress
  while polling:
    # query= "$where=created_date"
    # the format for different pages is to add an offset. our page size is 50000, so the next page is located 50000 away, so we will be incrementing by offset each time.
    query_url = "https://data.cityofnewyork.us/resource/i3j2-v52s.json?$limit=50000&$offset={}".format(offset)
    print "Queried: {}".format(query_url)

    # connect to Redis
    conn = redis.Redis(db=0)
    initial = time.time() #just to see how long it's taking each query
    response_dict = requests.get(query_url) # get the request
    print response_dict.status_code #see status code
    response_dict = response_dict.json() # cast to json
    print "figureed out response dict"
    # response_dict = response.json()
    count = len(response_dict)
    # if there isn't anything, stop running the loop
    if count <= 1:
      polling = False
    #get all the keys that exist so far in our db
    keys = conn.keys() #
    values = []
    if keys:
      # get all the values from the keys
      values = conn.mget(keys)
    # iterate through the response from the api call
    for result in response_dict:
      # for each complaint, log into redis
      # filtering for specific months
      # key: jan('-01-'), april('-04-'), july ('-07-'), october ('-10-')
      date = result['created_date']
      unique_key = result['unique_key'] #this is how we distinguish if something is in our Redis or not
      if '-01-' in date or '-04-' in date or '-07-' in date or '-10-' in date:
        if unique_key not in values: #make sure we don't have the complaint already logged
          if 'location' in result: #must have location so we can associate w/ neighborhood
            longitude = result['location']['longitude']
            latitude = result['location']['latitude']
            neighborhood = testLoc(longitude, latitude) #finds the neighborhood associated with the long, lat
            if neighborhood: #must have neighborhood so we can associate w/ other neighborhoods
              counter += 1 #increment total counter
              print "Adding new {} data to DB: {} \n".format(neighborhood, result)
              insert_key = "complaintID:{}".format(result['unique_key']) # we have it in as 'complaintID'+uniquekey so we know what we inserted & avoiding other possible conflicts or entries (not impossible)
              conn.rpush(neighborhood, (result['complaint_type'], insert_key, result['created_date'])) #add to list of neighborhoods in redis

    final = time.time() #how much time did it take for that entire batch of 50000
    print "Total Time: {} seconds".format(final-initial)
    print "Number of Entries: {} ".format(counter)
    offset += 50000 #inrement offset. still in while lot
    offset_iterator += 1 #increment how many times we have run the script
    print "# of times script succesfully run: {}".format(offset_iterator)


def get_realtime():
  #everything is the same as above with the exception that we only query once and check for today's numbers that we don't already have
  # Setup Redis Connection w/ different db
  conn2 = redis.Redis(db=1)
  # Load historical keys
  historical_keys = conn2.keys()
  historical_values = conn2.mget(historical_keys)

  # Load "Today"'s json aka latest 50,000 complaints (maximum fetch size)
  query_url = "https://data.cityofnewyork.us/resource/i3j2-v52s.json?$limit=50000"
  # Get the Response
  response = requests.get(query_url)
  response_dict = response.json()
  count = len(response_dict)
  # iterate through each of the 50,000 complaints
  for result in response_dict:
    # Check if there are any new entries
    # If there are, add to our historical database
    # If not, do nothing and move on
    if result['unique_key'] not in historical_values:
      longitude = result['location']['longitude']
      latitude = result['location']['latitude']
      neighborhood = testLoc(longitude, latitude)
      if neighborhood:
        print "Adding {} \n".format(result)
        # Redis insert
        ttl = 10
        conn2.setex(time.time(), neighborhood, ttl)
    else:
      continue

def testLoc(lon, lat):
  # print lon, lat
  lon = float(lon) #make sure it is a float
  lat = float(lat)
  q = {"geometry": {"$geoIntersects": { "$geometry": {"type": "Point", "coordinates": [lon, lat]}}}} #how we query mongo
  # print q
  geoJSON = coll.find_one(q) # find one thing that returned from the query
  if not geoJSON: # if no nhood found, we have to return nothing
    return None
  neighborhood = geoJSON['properties']['NTAName'] # get neighborhood name
  borough = geoJSON['properties']['BoroName'] #get borough name
  return "{n}/{b}".format(n=neighborhood,b=borough)

def main():
  # only run once
  get_historical_complaints()
  # get_realtime() # commented out because we don't use in our project

main()
