# polling-db
for streaming 311 complaints


Comparing periods of gentrification to our stats of how many complaints per neighborhood occured in various time periods from 2010-2015

Uses the NYC 311-Service-Requests-from-2010-to-Present API to get the number of complaints for all of New York City. Creates a Redis store full of NYC Complaint Data. It also uses a Flask app also that returns data on periods of gentrification & complaint information. Charted with pygal, external library. Link: http://www.pygal.org/en/latest/documentation/types/line.html.

## Analysis
### The Objective of `311.py`
The objective was originally to get historical 311 Complaints to understand the data around disinvestment in neighborhoods. We didn't filter out for specific complaints because we felt that if true disinvestment was happening in a neighborhood, it wouldn't just be housing specific complaints. We only collected in the months of January, April, July, and October for 2 reasons. 1) We didn't think we would see verifiable evidence of gentrification in such a smaller period than 3 months. and 2) Fetching the data would have taken an extra week due to the extremely high number of complaints. So what we got from this was
1) a way to look at where the complaints
2) a way to look at when complaints where happening
3) a way to look at what types of complaints were happening
4) a way to look at how many complaints were happening in 1-3 (i.e. how many & where, how many and when, & how many and what types)

### What we learned from `311.py` Redis Inputs
1) There are 188 neighborhoods in new york with a lot of housing complaints in the past 5 years

Using & Searching through a demographic document: <LINK>
2) The highest # of complaints per neighborhood per person for the most part usually come out of areas with higher Black & Latino populations
3) The lowest # of complaints per neighborhood per person for the most part usually come out of areas with higher Black & Latino populations
4) For neighborhoods with significant demographic change from 2000 to 2010 (highest percentage changes of Black/White/Asian/Latino) there were no specific spectrum of how those


### What we learned from `server.py` gentrification intervals
`oneyear.txt` + 311 complaints during those gentrifying periods
#### Average rate changes during one year intervals
|interval | previous | current
----------|----------|--------
|2010-2011 | None     | -12.76923077
|2011-2012 | -20.26666667  | -3.433333333
|2012-2013 | -4.866666667 | 14
|2013-2014 | 16.85185185 | 15.77777778
|2014-2015 | 17.29166667 | -10.58333333

These all have different start/ending gentrifying periods, but we saw a general trend for there to be a 'negative start' and a sharp upwards increase for 1 or two years, and then sharp decrease. However, we didn't know if this was strong enough to indicate a 'gentrifing factor' of having rate patterns similar for their interval comparison.
#### 1) We learned that we can't find an absolute gentrifying factor for 311 complaints

### What we learned from `server.py` line graph outputs
Because we have the ability to look at whatever list of neighborhoods we want and see their complaints over time, we learned a few things:
1) The trends of the complaint graphs are similar on average
2) Neighborhoods that have gentrified have different complaint counts per person than neighborhoods that have not gentrified.



