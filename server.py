import flask
import redis
import json
import pygal
from flask import request,jsonify
#from psycopg2 import connect, extras
from datetime import datetime
from pygal.style import DarkSolarizedStyle
app = flask.Flask(__name__)
conn = redis.Redis(db=0)
conn2 = redis.Redis(db=2)
from bson import json_util
import pprint
#
# Setup for DB
#
#def dict_cursor(conn, cursor_factory=extras.RealDictCursor):
#    return conn.cursor(cursor_factory=cursor_factory)

@app.route("/")
def index():
    q = request.args.get('q')
    final_thing = awesome()
    if q:
      final_thing=final_thing.get(q)
      return json.dumps(final_thing)
    
    return jsonify(final_thing)

@app.route("/graph")
def buildGraph():
    borough = request.args.getlist('b')
    n_list = request.args.getlist('n')
    years = ['2010', '2011', '2012', '2013', '2014', '2015']
    neighborhoods = conn.keys("*")
    neighborhoods = get_dup(neighborhoods)
    n_hoods = []
    b_list = []
    if borough:
        for n in neighborhoods:
	    if n.split('/')[1] in borough[0]:
		n_hoods.append(n)
	hood_complaints = get_x_y(n_hoods, years)
    elif n_list:
	for n in neighborhoods:
	    if n.split('/')[0] in n_list[0]:
		n_hoods.append(n)
	hood_complaints = get_x_y(n_hoods, years)
    else:
	hood_complaints = get_x_y(neighborhoods, years)
    bar_charts = []
    line_chart = pygal.Line(disable_xml_declaration=True)
    line_chart.title = 'Complaints Per Neighborhood by Intervals'
    line_chart.x_labels = years
    title = "Seeing 311"
    # line_chart.x_labels = map(str, range(int(years[0]), int(years[-1])))
    for hood in hood_complaints:
	line_chart.add(hood, hood_complaints[hood]['counts'])
    #for year in years:
      #counts, cities, total = get_per_year(neighborhoods, year)
      # create a bar chart
      #title = '311 Complaints For NYC Neighborhoods in {}'.format(year)
      #bar_chart = pygal.Bar(width=450, height=600,
      #                      explicit_size=True, title=title,
      #                      style=DarkSolarizedStyle,legend_at_bottom=True,
      #                      disable_xml_declaration=True, x_label_rotation=90, spacing=5, margin=5, pretty_print=True)
      #bar_chart = pygal.StackedLine(width=1200, height=600,
      #                      explicit_size=True, title=title, fill=True)
      #bar_chart.x_labels = cities[:10]
      #chart_string = 'Total: {}'.format(total)
      #bar_chart.add(chart_string, counts[:10])
      #bar_charts.append(bar_chart)
    return flask.render_template('index.html', bar_charts=bar_charts, title=title, line_chart=line_chart)

def get_dup(nhoods):
    n_dict = {}
    for n in nhoods:
	complaints = conn.lrange(n, 0, -1)
	seen = set()
	n_dict[n] = []
	n_dict[n] = [x for x in complaints if x not in seen and not seen.add(x)]
    return n_dict

def get_per_year(neighborhoods, year):
  neighborhoodsWithEdges = []
  nodeIndex = {}
  total = 0
  for hood in neighborhoods:
    nodeIndex[hood] = {'complaints':[], 'count':0, 'pop': 0}
    for tup in conn.lrange(hood, 0, -1):
      if year in tup:
	if tup not in nodeIndex[hood]['complaints']:
          nodeIndex[hood]['complaints'].append(tup)
          nodeIndex[hood]['count'] += 1
          total +=1

  comp_list = []
  for key, val in nodeIndex.iteritems():
    temp = {"hood": key, "count": val['count']}
    comp_list.append(temp)

  complaint_no = [i['count'] for i in comp_list]
  cities = [str(i['hood']) for i in comp_list]

  return complaint_no, cities, total

def get_x_y(hoods, years):
  final = []
  final_dict = {}
  ''' 'name': blah blah/Manhattan,
      'count':[500, 342, 434] '''
  number_finished = 0
  pop_dict = get_population()
  for hood in hoods:
    hood_name = hood.split('/')[0]
    if str(hood_name) in pop_dict:
      final_dict[hood] = {'name': hood, 'counts':[]}

      for year in years:
        count = 0
        for tup in conn.lrange(hood, 0, -1):
          if year in tup:
            count += 1
        ratio = 100 * count / float(pop_dict.get(hood_name, count))
        ratio = round(ratio, 2)
        final_dict[hood]['counts'].append(ratio)
        hoodb = hood.split('/')[0] + "/{}".format(year)
        print hoodb,count
        #conn2.set(hoodb,count)
    number_finished += 1
    print "{} has {} complaints pp!".format(hood, final_dict[hood]['counts'])
    print "{}/{} completed".format(number_finished,len(hoods))
  return final_dict

def get_mapping():
  with open('zillow_to_docp_mapping.json') as f:
    contents = json.load(f)

  pop_dict = {}
  for k,v in contents.iteritems():
    pop_dict[k] = v

  return pop_dict

def get_n_counts():
    final = {}
    neighborhoods = conn2.keys()
    for n in neighborhoods:
        count = int(conn2.get(n))
        n_hood,year = n.split('/')
        final[n] = count
    return final

def get_population():
  with open('population.json') as f:
    contents = json.load(f)['data']

  pop_dict = {}
  for i,stuff in enumerate(contents):
    if '2010' in contents[i]:
      pop_dict[str(stuff[12])] = int(stuff[13])

  return pop_dict

def get_n_counts():
    final = {}
    neighborhoods = conn2.keys()
    for n in neighborhoods:
        count = int(conn2.get(n))
        n_hood,year = n.split('/')
        final[n] = count
    return final
        
def get_gentrifying_periods(interval):
  if interval is not 'oneyear' and interval is not 'twoyears':
    return {}
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

def awesome():
  #neighborhoods = conn.keys("*")
  #neighborhoods = get_dup(neighborhoods)
  interval = 'oneyear'
  if interval == 'oneyear':
    years = ['2010','2011','2012','2013','2014','2015']
    n = 1
  else:
    years = ['2010','2012','2014']
    n= 2
  nhoods = get_n_counts()
  gent_periods = get_gentrifying_periods(interval)
  pp = pprint.PrettyPrinter(indent=4)
  final_thing = {}
  #pp.pprint(nhoods)
  # Our gent period neighborhoods have different keys than our neighborhood complaints, so we made mappings
  map_dict = get_mapping() #gent_period_keys:[n_hood_keys]
  for k,v in gent_periods.iteritems():
    if k in map_dict.keys():
      possible_keys = map_dict[k] 
      #pp.pprint(v)
      for key in possible_keys:
        starts = gent_periods.get(k)['start']
        ends = gent_periods.get(k)['end']
	for s,start in enumerate(starts):
	  for e,end in enumerate(ends):
	    if s == e:
	      start = start.year
	      end = end.year
	      # print start,end,key
	      # print nhoods
	      d2 = nhoods[str(key)+'/'+str(end)]
	      d1 = nhoods[str(key)+'/'+str(start)]
	      percent_change = 100 * (d2-d1)/d1
	      pd2 = nhoods.get(str(key)+'/'+str(int(end)-n))
	      pd1 = nhoods.get(str(key)+'/'+str(int(start)-n))
              previous = None
	      if pd2 and pd1:
		previous = 100 * (pd2-pd1)/pd1
	      print "Finding stuff for {}: {}% Change".format(str(key),percent_change)
	      if not str(key) in final_thing:
		final_thing[str(key)] = []
	      final_thing[str(key)].append({"start":start,"end":end,"delta":percent_change, "prev":previous})
  return final_thing
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
