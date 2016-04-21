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

    links = []

    neighborhoods = conn.keys("*")

    neighborhoodsWithEdges = []
    nodeIndex = {}

    # for each node we'll get the edges for that node, and add them
    # to the edge list
    for hood in neighborhoods:
	nodeIndex[hood] = {'complaints':[], 'count':0}
        for tup in conn.lrange(hood, 0, -1):
	        nodeIndex[hood]['complaints'].append(tup)
		nodeIndex[hood]['count'] += 1
            #weight = int(weight)
            #if weight > 2:
            #    if station not in nodeIndex:
            #        nodeIndex[station] = len(nodeIndex)
            #        stationsWithEdges.append(station)
            #    if target not in nodeIndex:
            #        nodeIndex[target] = len(nodeIndex)
            #        stationsWithEdges.append(target)
            #    links.append({"source":nodeIndex[station], "target":nodeIndex[target], "weight":weight})
            
    #nodes = [{"name":s, "group":0} for s in stationsWithEdges]
    #graph = {"links":links, "nodes":nodes}
    #print json.dumps(graph, indent=1)
    comp_list = []
    for key, val in nodeIndex.iteritems():
	temp = {"hood": key, "count": val['count']}
	comp_list.append(temp)
    cool = [i['count'] for i in comp_list]
    cities = [str(i['hood']) for i in comp_list]
    total = len(cool)
    #cool = cool[:5]
    #cities = cities[:5]
    #print cities
    # create a bar chart
    title = '311 Complaints For NYC Neighborhoods'
    bar_chart = pygal.Bar(width=1200, height=600,
                          explicit_size=False, title=title,
                          style=DarkSolarizedStyle,
                          disable_xml_declaration=True, x_label_rotation=90, spacing=5, margin=5, pretty_print=True)
    #bar_chart = pygal.StackedLine(width=1200, height=600,
    #                      explicit_size=True, title=title, fill=True)
    bar_chart.x_labels = cities
    bar_chart.add('No of Complaints', cool)
    return flask.render_template('index.html', nodeIndex=nodeIndex, bar_chart=bar_chart, title=title)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
