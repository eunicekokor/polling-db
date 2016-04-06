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

# We will process the CSV
def get_historical_complaints():
  query_url = "https://data.cityofnewyork.us/resource/i3j2-v52s.json?$limit=50000&$offset=100000"
  # $offset=0
  # query_url = "https://api.github.com/search/repositories?q=tetris+language:assembly&sort=stars&order=desc"
  # initial = time.time()
  response = requests.get(query_url)
  response_dict = response.json()
  count = len(response_dict)

  for result in response_dict:
    if 'Unspecified' not in result['school_region']:
      print str(result) + '\n'
    # changed_result = {"latitude": result['latitude'], "longitude": result['longitude']}
    # Info We Care About
    # street_name

  # final = time.time()
  # print "Total Time: {} seconds".format(final-initial)
  # print "Number of Entries: {} ".format(count)


def get_realtime():
  # Load historical
  historical = {}
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
    if result['unique_key'] not in historical:
      historical['unique_key'] = result
      # Redis connect and insert

    print str(result) + '\n'
  # Use redis
  return "hello"

def main():
  # only run once
  get_historical_complaints()


main()
