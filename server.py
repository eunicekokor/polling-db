import flask
import redis
import json
import pygal
from pygal.style import DarkSolarizedStyle
app = flask.Flask(__name__)
conn = redis.Redis(db=0)

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/graph")
def buildGraph():

    years = ['2014', '2015', '2016']
    neighborhoods = conn.keys("*")
    bar_charts = []
    for year in years:
      counts, cities, total = get_per_year(neighborhoods, year)
      # create a bar chart
      title = '311 Complaints For NYC Neighborhoods in {}'.format(year)
      bar_chart = pygal.Bar(width=1200, height=600,
                            explicit_size=False, title=title,
                            style=DarkSolarizedStyle,
                            disable_xml_declaration=True, x_label_rotation=90, spacing=5, margin=5, pretty_print=True)
      #bar_chart = pygal.StackedLine(width=1200, height=600,
      #                      explicit_size=True, title=title, fill=True)
      bar_chart.x_labels = cities[:5]
      chart_string = 'No of Complaints out of {}'.format(total)
      bar_chart.add(chart_string, counts[:5])
      bar_charts.append(bar_chart)
    return flask.render_template('index.html', bar_charts=bar_charts, title=title)

def get_per_year(neighborhoods, year):
  neighborhoodsWithEdges = []
  nodeIndex = {}
  total = 0

  for hood in neighborhoods:
    nodeIndex[hood] = {'complaints':[], 'count':0, 'pop': 0}
    for tup in conn.lrange(hood, 0, -1):
      if year in tup and '-04-' in tup:
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

def get_n_y(nodeIndex, hood, year):
  return None

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
