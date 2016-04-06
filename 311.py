import requests
import time
import redis
geojson = {}
json = {}
####################
# Info We Care About Retreiving from this fetch
# latitude, longitude, street_name, zip_code, complaint_type, created_date
# street_name
# if complaint is a school complaint (to see if there more/less resources in certain areas)
# we care about

def get_historical_complaints():
  polling = True
  offset=50000
  while polling:
    # query= "$where=created_date"
    query_url = "https://data.cityofnewyork.us/resource/i3j2-v52s.json?$limit=50000&$offset={}".format(offset)
    print "Queried: {}".format(query_url)
    initial = time.time()
    response = requests.get(query_url)
    response_dict = response.json()
    count = len(response_dict)
    if count <= 1:
      polling = False

    for result in response_dict:
      # for each complaint, log into redis
      # filtering for specific months
      # key: jan('-01-'), april('-04-'), july ('-07-'), october ('-10-')
      date = result['created_date']
      if '-01-' in date or '-04-' in date or '-07-' in date or '-10-' in date:
        print "Adding {} \n".format(result)
        conn = redis.Redis()
        conn.set(result['unique_key'], result)

    final = time.time()
    print "Total Time: {} seconds".format(final-initial)
    print "Number of Entries: {} ".format(count)
    offset += 50000


def get_realtime():
  # Setup Redis Connection
  conn = redis.Redis()
  # Load historical keys
  historical_keys = conn.keys()
  # values = conn.mget(historical_keys)

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
    if result['unique_key'] not in historical_keys:
      print "Adding {} \n".format(result)
      # Redis insert
      conn.set(result['unique_key'], result)
    else:
      continue

def main():
  # only run once
  get_historical_complaints()
  # get_realtime()

main()
