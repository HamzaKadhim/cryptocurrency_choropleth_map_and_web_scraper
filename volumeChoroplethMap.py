import requests, pymysql, csv, pycountry, datetime
import plotly.express as px, pandas as pd

class VolumeChoroplethMapSetter:
	"""Contains all the methods needed to plot a volume choropleth map."""

	def __init__(self):
		"""Define variables to be used."""
		self.exchangeName = []
		self.exchangeCountry = []
		self.exchangeVolume = []																
		self.knownCountryExchanges = []
		self.uniqueCountries = []
		self.uniqueVolumes = []
		self.iso_codes = []
		self.countryAndVolume = []		
		self.dbServerName = "127.0.0.1"
		self.dbUser = "root"
		self.dbPassword = "****"	# Insert mySQL password here.
		self.dbName = "exchange_data"	# Create this database on mySQL.
		self.charSet = "utf8mb4"														 

	def _apiRetrieval(self):
		"""Retrieves and appends info from over 300 exchanges
		 using the coingecko API."""
		urlPageOne = "https://api.coingecko.com/api/v3/exchanges?per_page=250"
		urlPageTwo =	( 
		"https://api.coingecko.com/api/v3/exchanges?per_page=250&page=2")
		urlPageOneRequest = requests.get(urlPageOne)
		urlPageOneResponseList = urlPageOneRequest.json()
		urlPageTwoRequest = requests.get(urlPageTwo)
		urlPageTwoResponseList = urlPageTwoRequest.json()

		for i in range(0, len(urlPageOneResponseList)):
			self.exchangeName.append(urlPageOneResponseList[i]['name'])
			self.exchangeCountry.append(urlPageOneResponseList[i]
										['country'])
			self.exchangeVolume.append(round(urlPageOneResponseList[i]
										['trade_volume_24h_btc']))

		for i in range(0, len(urlPageTwoResponseList)):
			self.exchangeName.append(urlPageTwoResponseList[i]['name'])
			self.exchangeCountry.append(urlPageTwoResponseList[i]
										['country'])
			self.exchangeVolume.append(round(urlPageTwoResponseList[i]
										['trade_volume_24h_btc']))

	def _arrangeExchanges(self):
		"""Rearranges exchange lists according to descending order of volume
			and discards exchanges with unknown origin countries."""
		self._apiRetrieval()

		zipped = sorted(zip(self.exchangeVolume, self.exchangeName, 
							self.exchangeCountry))
		zipped.reverse()
		for i in range(0, len(zipped)):
			if zipped[i][2] != None:
				self.knownCountryExchanges.append(zipped[i])

		self.exchangeVolume, self.exchangeName, self.exchangeCountry = zip(*
													self.knownCountryExchanges)

	def createSQLExchangeTable(self):
		"""Creates an SQL database table that will hold each exchange with 
		its volume and country as well as the current timestamp."""
		connectionObject = pymysql.connect(host=self.dbServerName, 
											user=self.dbUser,
											password = self.dbPassword,
											db=self.dbName,
											charset=self.charSet)
		cursorObject = connectionObject.cursor()

		createStatement = """CREATE TABLE exchanges
							(exchange_id SMALLINT UNSIGNED AUTO_INCREMENT,
							exchange_name VARCHAR(100),
							exchange_country VARCHAR(100),
							exchange_volume MEDIUMINT UNSIGNED,
							time_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
							CONSTRAINT pk_exchanges PRIMARY KEY (exchange_id)
							)"""

		cursorObject.execute(createStatement)

		connectionObject.commit()
		connectionObject.close()

	def insertSQLExchangeTable(self):
		"""Insert excchange data into the SQL database exchange table."""
		self._arrangeExchanges()

		connectionObject = pymysql.connect(host=self.dbServerName, 
											user=self.dbUser,
											password = self.dbPassword,
											db=self.dbName,
											charset=self.charSet)
		cursorObject = connectionObject.cursor()

		for i in range (0, len(self.exchangeName)):
			insertStatement = f"""INSERT INTO exchanges
							(exchange_id, exchange_name, exchange_country,
							exchange_volume, time_fetched)
							VALUES (null, "{self.exchangeName[i]}",
							"{self.exchangeCountry[i]}",
							{self.exchangeVolume[i]}, now())"""

			cursorObject.execute(insertStatement)

		connectionObject.commit()
		connectionObject.close()

	def _setCountryVolumes(self):
		"""Finds the total volume of each country using the exchange lists."""
		self._arrangeExchanges()
		# Referenced by the iterator. Used to determine the index of the
		# duplicate country.
		iteratedCountries = []
		for country in self.exchangeCountry:
			elemIndex = self.exchangeCountry.index(country)
			iteratedCountries.append(self.exchangeCountry[elemIndex])

			if country in self.uniqueCountries:
				uniqueIndex = self.uniqueCountries.index(country)
				# Finds the index value of the current iteration of the country
				# string.
				countryIndexFinder = iteratedCountries.count(country)
				countryIndexPosition = [i for i, n in 
										enumerate(self.exchangeCountry) if 
										n == country][countryIndexFinder-1]
				# The volume value of the duplicate country is added to the
				# unique country's total volume.
				self.uniqueVolumes[uniqueIndex] = self.uniqueVolumes[
													uniqueIndex] + \
													self.exchangeVolume[
													countryIndexPosition]

			elif country not in self.uniqueCountries:
				self.uniqueCountries.append(self.exchangeCountry[elemIndex])
				self.uniqueVolumes.append(self.exchangeVolume[elemIndex])

		# Countries and volumes are sorted in descending order of volume.		
		self.uniqueCountries = [x for _,x in sorted(zip(self.uniqueVolumes,
														self.uniqueCountries),
														reverse=True)]
		self.uniqueVolumes.sort(reverse=True) 

	def createSQLCountryTable(self):
		"""Creates an SQL database table that will hold each country
		and its total volume."""
		connectionObject = pymysql.connect(host=self.dbServerName, 
											user=self.dbUser,
											password = self.dbPassword,
											db=self.dbName,
											charset=self.charSet)
		cursorObject = connectionObject.cursor()

		createStatement = """CREATE TABLE exchange_volume_by_country 		
						(country_id SMALLINT UNSIGNED AUTO_INCREMENT,
						country_name VARCHAR(100),
						country_volume MEDIUMINT UNSIGNED,
						time_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
						CONSTRAINT pk_exchange_volume_by_country
						PRIMARY KEY (country_id)
						)"""

		cursorObject.execute(createStatement)

		connectionObject.commit()
		connectionObject.close()

	def insertSQLCountryTable(self):
		"""Inserts the country/volume data into the SQL database table"""
		self._setCountryVolumes()

		connectionObject = pymysql.connect(host=self.dbServerName, 
											user=self.dbUser,
											password = self.dbPassword,
											db=self.dbName,
											charset=self.charSet)
		cursorObject = connectionObject.cursor()

		for i in range (0, len(self.uniqueCountries)):
			insertStatement = f"""INSERT INTO exchange_volume_by_country
							(country_id, country_name, country_volume,
							time_fetched)
							VALUES (null, "{self.uniqueCountries[i]}",
							"{self.uniqueVolumes[i]}", now())"""

			cursorObject.execute(insertStatement)

		connectionObject.commit()
		connectionObject.close()

	def _getISOCode(self):
		"""Convert country's English short name to its ISO alpha-3 code
		which is necessary in order to plot the plotly choropleth world map."""
		self._setCountryVolumes()
		country_iso = {}
		for country in pycountry.countries:
			country_iso[country.name] = country.alpha_3

		self.iso_codes = [country_iso.get(country, 'Unknown code') for country
		 in self.uniqueCountries]
		# Some countries' common names (which are used by the coingecko API)
		# are different from their English short name values, so they cannot be
		# converted to ISO code. In this case, the ISO codes are hard coded in,
		# although ideally a module would exist that allows for common country
		# names to be directly converted to ISO code (the pycountry module
		# functionality for this is  not very reliable.) 
		for i in range(0, len(self.iso_codes)):
			if self.iso_codes[i] == 'Unknown code':
				indexOfUnknownCountry = self.iso_codes.index(self.iso_codes[i])
				if self.uniqueCountries[indexOfUnknownCountry] == (
															"South Korea"):
					self.iso_codes[i] = 'KOR'
				elif self.uniqueCountries[indexOfUnknownCountry] == (
													"British Virgin Islands"):
					self.iso_codes[i] = 'VGB'
				elif self.uniqueCountries[indexOfUnknownCountry] == "Vietnam":
					self.iso_codes[i] = 'VNM'
				elif self.uniqueCountries[indexOfUnknownCountry] == "Russia":
					self.iso_codes[i] = 'RUS'
				elif self.uniqueCountries[indexOfUnknownCountry] == "Taiwan":
					self.iso_codes[i] = 'TWN'
		
	def _prepareCountryVolumeCsv(self):
		"""The country names, volumes, and ISO codes are stored within nested
		lists which themselves are stored inside a single list. This list will
		later be used to write a csv file of these elements."""
		self._getISOCode()

		for i in range(0, len(self.uniqueCountries)):
			countryList = []
			countryList.append(self.uniqueCountries[i])
			countryList.append(self.uniqueVolumes[i])
			countryList.append(self.iso_codes[i])
			self.countryAndVolume.append(countryList)
		
	def exchangeVolumeCsvWriter(self, filename):
		"""Writes the individual exchange names, volumes, and countries to a 
		csv file. Not needed for choropleth map. Optional to call."""
		self._arrangeExchanges()
		header = ["volume", "name", "country"]
		with open(filename, "w", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(header)
			writer.writerows(self.knownCountryExchanges)

	def _countryVolumeCsvWriter(self, filename):
		"""Writes the individual country names, volumes, and ISO codes to a
		csv file which will then be used to plot the plotly choropleth world
		map."""
		self._prepareCountryVolumeCsv()
		header = ["country", "volume", "iso_alpha"]
		with open(filename, "w", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(header)
			writer.writerows(self.countryAndVolume)

	def choroplethMapPlotter(self, filename):
		"""Plots the choropleth world map according to country volume."""
		self._countryVolumeCsvWriter(filename)
		dateToConvert = datetime.datetime.now()
		date = dateToConvert.strftime('%Y/%m/%d')
		df = pd.read_csv(filename, dtype={"country": str})
		fig = px.choropleth(df, locations="iso_alpha", color="volume",
			title=f"Cryptocurrency Exchange Volumes (in Bitcoin) on {date}",
						hover_name="country",
						color_continuous_scale=px.colors.sequential.Plasma)
		fig.show()


if __name__ == '__main__':
	# The SQL methods for the different tables must be called using 
	# different instances, otherwise helper methods called within the insert
	# SQL methods would be unnecessarily called twice, resulting in an error.
	# It is the same case for the csv file writer methods.
	instanceOne = VolumeChoroplethMapSetter()
	instanceTwo = VolumeChoroplethMapSetter()
	instanceThree = VolumeChoroplethMapSetter()
	instanceFour = VolumeChoroplethMapSetter()
	#instanceFive = volumeChoroplethMapSetter()
	instanceOne.createSQLExchangeTable()
	instanceOne.insertSQLExchangeTable()
	instanceTwo.createSQLCountryTable()
	instanceTwo.insertSQLCountryTable()
	instanceThree.exchangeVolumeCsvWriter('exchangevolumes.csv')
	#instanceFive.countryVolumeCsvWriter('countryvolumes.csv')
	instanceFour.choroplethMapPlotter('countryvolumes.csv')

	# Note that small countries such as Cayman Islands unfortunately are not
	# visible on the plotly world map despite having very high volumes.

	# Perhaps it would be better to write and then read the csv files first,
	# and then add the csv data to SQL, rather than directly writing the
	# lists/tuples to SQL, because then the entire class could be run in a 
	# single instance.
	




