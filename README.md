# volumeChoroplethMap.py

This file fetches exchanges names, 24 hour volumes, and origin countries from
the coingecko API, stores them in an SQL database, writes them to CSV files,
and uses the values to produce a choropleth world map using plotly, showing
the 24 hour cryptocurrency exchange volumes for each country on the world map
with a colorscale. Two SQL tables are created and populated as well as two
CSV files. The first table contains each exchange name with its respective
country and 24 hour volume. The second table contains each country with its
total 24 hour volume (volumes from exchanges within the same country are
summed.) The same information composes the CSV files. Unfortunately countries
with small land-areas such as Seychelles and Cayman Islands are not included
within plotly's world map, despite these countries having some of the largest
volumes of cryptocurrency transactions in the world. This will require a 
solution in future updates. Modules and libraries used in this file include
requests, csv, pymysql, pycountry, datetime, plotly.express and pandas. 

# pageViewPlotter.py

This file scrapes the exchange section of the coingecko website using
beautiful soup to obtain the top 10 cryptocurrency exchanges with the highest
volumes. The exchanges'"about" sections are then scraped to obtain the recent
monthly pageviews, which are then summed together. The total monthly pageviews 
of the top 10 exchanges are then paired with their respective months, and
plotted using matplotlib. This plot, if populated with information from many
months, can be used to gouge the rise and fall of cryptocurrency popularity
through time, and it can also be used to find a correlation with
cryptocurrency price movements. Modules and libraries used in this file include
bs4, requests, re (regex), datetime, csv, matplotlib.pyplot, and pandas.
