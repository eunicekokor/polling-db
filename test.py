import json

with open('population.json') as f:
  contents = json.load(f)['data']

pop_dict = {}
for i,stuff in enumerate(contents):
  if '2010' in contents[i]:
    pop_dict[str(stuff[12])] = int(stuff[13])

