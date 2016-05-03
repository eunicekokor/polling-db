import flask
import redis
import json
import pygal
from flask import request,jsonify,Response
from datetime import datetime
from pygal.style import DarkSolarizedStyle
app = flask.Flask(__name__)
conn = redis.Redis(db=0)
conn2 = redis.Redis(db=2)
from bson import json_util
import pprint

# charted with pygal, external library. Link: http://www.pygal.org/en/latest/documentation/types/line.html

@app.route("/")
def index():
    ''' Building a json response based on url arguments'''
    # two ways we can input into the url will be ?p=(oneyear or twoyears) or ?q=Neighborhood NAme
    # p = period/interval and there are only two options. q = neighborhood name and one can choose from all neighborhoods we have & have to be precise by name
    q = request.args.get('q')
    period = request.args.get('p')
    # if we get a specific interval period as an argument, we have to fetch our data based on it being one year or two years
    if period:
    	final_thing = awesome(period)
    else:
	final_thing = awesome(None) #if no interval period, just use no argument
    if q:
      final_thing=final_thing.get(q) #if someone is looking for a specific neighborhood, get that from the dictionary and have it's list of interval & percentages outputted
      return Response(json.dumps(final_thing), mimetype='application/json')
    #final_thing has all of our gentrified periods and their complaint changes in percent `delta` and `prev` (see README and below for exact definitions)
    return jsonify(final_thing)

@app.route("/graph")
def buildGraph():
    ''' building line graphs based on arguments and existing data '''

    # if someone inputs n (neighborhood/list of neighborhoods)
    n_list = request.args.getlist('n')
    years = ['2010', '2011', '2012', '2013', '2014', '2015'] #x axis for graph
    # neighborhoods = conn.keys("*")
    # neighborhoods = get_dup(neighborhoods)
    nbhs = get_n_counts() # Dictionary that is formatted as `Neighborhood Name/Year: Total Complaints From that Year`
    final_list = {}
    hood_complaints = {}
    # iterate through all keys and values in the dictionary of 311 Complaints & create an output
    ''' Format of the output we are creating -->
      'name': Morningside/Manhattan,
      'count':[500, 342, 434]
    '''
    for nbh,v in nbhs.iteritems():
        name = nbh.split('/')[0] #Neighborhood Name
        year = nbh.split('/')[1] #Year
        i=years.index(year) # a way to figure out which year it will be displayed on the graph
	if name not in final_list:
	    final_list[name] = [None] * 6 #add an empty array with exactly 6 spots for 6 years
        final_list[name][i] = nbhs[nbh] # put complaint in appropriate position in array
    if n_list:
      # if someone adds narrowing neighborhoods
      arglist = n_list[0]
      arglist = arglist.split(',') # if there are multiple iterate
      for n in arglist:
        #print final_list
	if n in final_list.keys(): #if that neighborhood is in our dictionary of neighborhoods and complaints
          hood_complaints[n] = final_list[n] # add to final dictionary, hood complaints
    else: #if nothing else specified just output our list
      hood_complaints = final_list
    bar_charts = [] # From pygal documentation
    line_chart = pygal.Line(disable_xml_declaration=True)
    line_chart.title = 'Complaints Per Neighborhood by Intervals'
    line_chart.x_labels = years
    title = "Seeing 311"
    # line_chart.x_labels = map(str, range(int(years[0]), int(years[-1])))
    for hood in hood_complaints:
	line_chart.add(hood, hood_complaints[hood])

    return flask.render_template('index.html', bar_charts=bar_charts, title=title, line_chart=line_chart)

# checking if we have any duplicate complaints in our database to be safe
# we get a list of all values per key and use a list comprehension to only add the ones that were seen once
def get_dup(nhoods):
    n_dict = {}
    for n in nhoods:
	complaints = conn.lrange(n, 0, -1)
	seen = set()
	n_dict[n] = []
	n_dict[n] = [x for x in complaints if x not in seen and not seen.add(x)]
    return n_dict

# we run this once to get the total # of complaints per neighborhood per year per neighborhood.
# This took over 1 minute each time, so we only ran one and added to a Redis store
def get_x_y(hoods, years):
  final = []
  final_dict = {}

  number_finished = 0
  pop_dict = get_population() # this is the populations of each neighborhood
  for hood in hoods:
    hood_name = hood.split('/')[0]
    if str(hood_name) in pop_dict: #only add the ones we have populations for
      final_dict[hood] = {'name': hood, 'counts':[]}

      for year in years: # for each year, calculate the count of complaints with the year in that complaint
        count = 0
        for tup in conn.lrange(hood, 0, -1): # tuple looks like (complaintID:381014, date_create:dateobject, 'HEATING')
          if year in tup:
            count += 1
        ratio = 100 * count / float(pop_dict.get(hood_name, count)) #calculate year ratio
        ratio = round(ratio, 2)
        final_dict[hood]['counts'].append(ratio)
        hoodb = hood.split('/')[0] + "/{}".format(year)
        '''put into our Redis DB 2 & is represented like `Neighborhood/201X : number` where number is the count of complaints in that year, 201X is the year in question, and Neighborhood is the name of the neighborhood
        We also used to add it to redis, as we only ran this one time, so below is the debugging for this
        #print hoodb,count
        #conn2.set(hoodb,count) '''
    number_finished += 1
    print "{} has {} complaints pp!".format(hood, final_dict[hood]['counts'])
    print "{}/{} completed".format(number_finished,len(hoods))
  return final_dict

''' This is important because our Zillow neighborhood mappings are different than our neighborhoods mapping, so we accounted for all the differnces and use this when we're analyzing gentrifiation intervals '''
def get_mapping():
  with open('zillow_to_docp_mapping.json') as f:
    contents = json.load(f)

  pop_dict = {}
  for k,v in contents.iteritems():
    pop_dict[k] = v

  return pop_dict

''' Returns neighborhoods in the format:
      {"Neighborhood/Year" : Count}
      Where count is the # of complaints from that year'''
def get_n_counts():
    final = {}
    neighborhoods = conn2.keys()
    for n in neighborhoods:
        count = int(conn2.get(n))
        n_hood,year = n.split('/')
        final[n] = count
    return final

# This function fetches the population counts for each neighborhood.
def get_population():
  with open('population.json') as f:
    contents = json.load(f)['data']

  pop_dict = {}
  for i,stuff in enumerate(contents):
    if '2010' in contents[i]:
      pop_dict[str(stuff[12])] = int(stuff[13])

  return pop_dict


''' This is the most 2nd important function for analyzing specifically the gentrified periods
First we get whichever interval we are interested either oneyear or twoyears. Then we parse
the text file to figure out starting & ending periods and the neighborhood and returns a dictionary
of populated `neighborhood: start: [2012, 2013], end: [2013,2014]` entries.
'''
def get_gentrifying_periods(interval):
  with open(interval + '.txt') as f:
    contents = f.readlines()
  index = 1

  pop_dict = {}
  keystuff = ""
  for line in contents:
    if index == 1:
      keystuff = line.replace('\n', '')
      if keystuff not in pop_dict:
      	pop_dict[keystuff] = {"start":[], "end":[]}
    if index == 2:
      # pop_dict[keystuff]['start'] = datetime.strptime(line, '%c')
      # print pop_dict[line]['start']
      line = line.replace(' GMT+0000 (UTC)', '')
      line = line.replace('\n', '')
      pop_dict[keystuff]['start'].append(datetime.strptime(line, '%a %b %d %Y %X'))
      #Sat Jan 31 2015 00:00:00 GMT+0000 (UTC)

    if index == 3:
      line = line.replace(' GMT+0000 (UTC)', '')
      line = line.replace('\n', '')

      pop_dict[keystuff]['end'].append(datetime.strptime(line, '%a %b %d %Y %X'))
      index = 0
    index += 1
  return pop_dict

''' This is the most important function for analyzing specifically the gentrified periods
 `Neighborhood: start: [YearStart, YearStart], end: [YearEnd,YearEnd]` entries. Depending on the interval, there are different year values we will get 311 complaint values for.
'''
def awesome(inter):
  #neighborhoods = conn.keys("*")
  #neighborhoods = get_dup(neighborhoods)
  print inter
  if not inter:
    interval = 'oneyear'
  else:
    interval = str(inter)
  if interval == 'oneyear':
    years = ['2010','2011','2012','2013','2014','2015']
    n = 1
  else:
    years = ['2010','2012','2014']
    n= 2
  nhoods = get_n_counts() # Like {"Neighborhood/Year" : Count}
  gent_periods = get_gentrifying_periods(interval) # like {Neighborhood: 'start': [YearStart, YearStart], 'end': [YearEnd,YearEnd]}
  # pp value will just be for debugging
  pp = pprint.PrettyPrinter(indent=4)
  final_thing = {} # where we will be putting all of our percent changes
  #pp.pprint(nhoods)
  # Our gent period neighborhoods have different keys than our neighborhood complaints, so we made mappings
  # We are only getting gentrification intervals for the ones in our text files
  map_dict = get_mapping() #gent_period_keys:[n_hood_keys]
  for k,v in gent_periods.iteritems():
    if k in map_dict.keys():
      possible_keys = map_dict[k]
      #print possible_keys
      #pp.pprint(v)
      for key in possible_keys: #iterate through the neighborhoods that we have
        starts = gent_periods.get(k)['start'] # this is a list of start of gentrification periods
        ends = gent_periods.get(k)['end'] # this is a list of ends of gentrification periods
	for s,start in enumerate(starts):
	  for e,end in enumerate(ends):
	    if s == e: #make sure we are looking at the same start / end period
	      start = start.year #datetime object to year as a string
	      end = end.year #datetime object to year as a string
	      # print start,end,key
	      # print nhoods
        #since nhoods looks like {"Neighborhood/Year" : Count} to get the count of start/end, we have to format it in that way
	      d2 = nhoods[str(key)+'/'+str(end)]
	      d1 = nhoods[str(key)+'/'+str(start)]
	      percent_change = 100 * (d2-d1)/d1 # Our method of determining % change from start to end
	      pd2 = nhoods.get(str(key)+'/'+str(int(end)-n)) # if there is a previous interval, get the percent change for that interval. n = 2 or 1 depending on twoyears or oneyear interval
	      pd1 = nhoods.get(str(key)+'/'+str(int(start)-n))
              previous = None
	      if pd2 and pd1:
		previous = 100 * (pd2-pd1)/pd1
	      #print "Finding stuff for {}: {}% Change".format(str(key),percent_change)
        #add gentrification to our final interval and we are calculating % change & previous percent change
	      if not str(key) in final_thing:
		final_thing[str(key)] = []
	      final_thing[str(key)].append({"start":start,"end":end,"delta":percent_change, "prev":previous})
  return final_thing
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
