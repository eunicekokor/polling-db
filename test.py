from datetime import datetime

def get_gentrifying_periods():
  with open('oneyear.txt') as f:
    line = f.readline()
    index = 1

    pop_dict = {}
    keystuff = ""

    if index == 1:
      keystuff = line.replace('\n', '')
      pop_dict[keystuff] = []

    if index == 2:
      # pop_dict[keystuff]['start'] = datetime.strptime(line, '%c')
      # print pop_dict[line]['start']
      line1 = line.replace(' GMT+0000 (UTC)', '')
      line1 = line1.replace('\n', '')

      #Sat Jan 31 2015 00:00:00 GMT+0000 (UTC)
      line2 = f.readline()
      line2 = line2.replace(' GMT+0000 (UTC)', '')
      line2 = line2.replace('\n', '')

      pop_dict[keystuff].append({"start": datetime.strptime(line1, '%a %b %d %Y %X'), "end":datetime.strptime(line2, '%a %b %d %Y %X')})

      index = 0

    line = f.readline()
    index += 1

  return pop_dict

print get_gentrifying_periods()
