from datetime import datetime

def get_gentrifying_periods():
  with open('oneyear.txt') as f:
    contents = f.readlines()
  index = 1

  pop_dict = {}
  keystuff = ""
  for line in contents:
    if index == 1:
      keystuff = line.replace('\n', '')
      pop_dict[keystuff] = {"start": None, "end": None}

    if index == 2:
      # pop_dict[keystuff]['start'] = datetime.strptime(line, '%c')
      # print pop_dict[line]['start']
      line = line.replace(' GMT+0000 (UTC)', '')
      line = line.replace('\n', '')

      pop_dict[keystuff]['start'] = datetime.strptime(line, '%a %b %d %Y %X')
      #Sat Jan 31 2015 00:00:00 GMT+0000 (UTC)

    if index == 3:
      line = line.replace(' GMT+0000 (UTC)', '')
      line = line.replace('\n', '')

      pop_dict[keystuff]['end'] = datetime.strptime(line, '%a %b %d %Y %X')
      index = 0
    index += 1

  return pop_dict
