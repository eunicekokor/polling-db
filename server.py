import flask
import redis
import json
import pygal
from flask import request
from pygal.style import DarkSolarizedStyle
app = flask.Flask(__name__)
conn = redis.Redis(db=0)

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/graph")
def buildGraph():
    borough = request.args.get('b')
    years = ['2014-01', '2015-01', '2016-01']
    neighborhoods = conn.keys("*")
    bar_charts = []
    line_chart = pygal.Line(disable_xml_declaration=True)
    line_chart.title = 'Complaints Per Neighborhood by Intervals'
    line_chart.x_labels = years
    title = "Seeing 311"
    # line_chart.x_labels = map(str, range(int(years[0]), int(years[-1])))
    hood_complaints = get_x_y(neighborhoods, years)
    for hood in hood_complaints:
        if borough:
	    if borough in hood:
	        line_chart.add(hood, hood_complaints[hood]['counts'])
	else:
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

def get_per_year(neighborhoods, year):
  neighborhoodsWithEdges = []
  nodeIndex = {}
  total = 0

  for hood in neighborhoods:
    nodeIndex[hood] = {'complaints':[], 'count':0, 'pop': 0}
    for tup in conn.lrange(hood, 0, -1):
      if year in tup:
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
	'count':[500, 342, 434]'''
    for hood in hoods:
	final_dict[hood] = {'name': hood, 'counts':[]}
	for year in years:
            count = 0
            for tup in conn.lrange(hood, 0, -1):
	        if year in tup:
		    count += 1
	    final_dict[hood]['counts'].append(count)
    return final_dict

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
