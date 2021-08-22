import bs4, requests, re, datetime, csv
import matplotlib.pyplot as plt
from pandas import *


class TotalViewsScraper:
	"""Collects the total page views of the day for the to 10 exchanges on 
	coingecko with the highest trading volumes."""

	def __init__(self):
		"""Defines lists that will store total page views at specific
		dates."""
		self.exchangeViewsByDay = []
		self.dateOfViews = []
		self.exchangeViewsAndDate = []

	def _getViews(self):
		"""Scrapes the total page views for the top 10 exchanges for the day
		and appends them to a list."""
		listHolder = []
		totalExchangeViews = 0
		exchangeCounter = 1		# Used by the bs4 scraper.

		for i in range(0,10):
			link = "https://www.coingecko.com/en/exchanges"
			res = requests.get(link)
			res.raise_for_status()
			exchangePage = bs4.BeautifulSoup(res.text, 'html.parser')
			exchangehref = exchangePage.find_all("tr")[exchangeCounter].select(
															"a")[0].get("href")
			exchangeNameFinder = exchangehref.rfind('/')
			exchangeName = exchangehref[exchangeNameFinder:]
			print(exchangeName)
			exchangeLink = link + exchangeName + "#about"
			res = requests.get(exchangeLink)
			res.raise_for_status()
			exchangeAboutPage = bs4.BeautifulSoup(res.text, 'html.parser')

			pageViewsSelector = exchangeAboutPage.find_all(class_=
										"col-12 col-md-6 col-lg-4 mt-3")[12]
			exchangeViewsText = pageViewsSelector.get_text()
			numberRegex = re.findall('[0-9]+', exchangeViewsText)
			del numberRegex[-1]
			exchangeViews = ''.join(numberRegex)
			exchangeViews = int(exchangeViews)
			totalExchangeViews = totalExchangeViews + exchangeViews 
			exchangeCounter = exchangeCounter + 1
			print(totalExchangeViews)

		listHolder.append(totalExchangeViews)
		dateToConvert = datetime.datetime.now()
		date = dateToConvert.strftime('%Y/%m/%d')
		listHolder.append(date)
		self.exchangeViewsAndDate.append(listHolder)

	def writeExchangePageViewsCsv(self, filename):
		"""Writes a csv file to store the total page views for the top 10
		 exchanges with their corresponding dates."""
		self._getViews()
		header = ["exchange_views", "date"]
		with open(filename, "w", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(header)
			writer.writerows(self.exchangeViewsAndDate)

	def appendExchangePageViewsCsv(self, filename):
		"""Appends the csv file with today's total page views."""
		self._getViews()
		with open(filename, "a", newline="") as f:
			writer = csv.writer(f)
			writer.writerows(self.exchangeViewsAndDate)

	def _readCsvData(self, filename):
		"""Uses pandas to read the csv file, who's data is to be plotted."""
		data = read_csv(filename)
		self.exchangeViewsByDay = data['exchange_views'].tolist()
		self.dateOfViews = data['date'].tolist()


	def plotExchangePageViews(self, filename):
		"""Plots the exchange views per date using matplotlib."""
		self._readCsvData(filename)
		plt.style.use('seaborn')
		fig, ax = plt.subplots()
		ax.plot(self.dateOfViews, self.exchangeViewsByDay, linewidth=3)

		ax.set_title("Exchange Views by Date", fontsize=24)
		ax.set_xlabel("Date", fontsize=14)
		ax.set_ylabel("Exchange Views", fontsize=14)
		ax.tick_params(axis='y', labelsize=14)
		ax.tick_params(axis='x', labelsize=10)

		plt.show()

		# Tick labelling will need to be adjusted if many values are being 
		# plotted.

if __name__ == '__main__':
	instanceOne = TotalViewsScraper()
	#instanceTwo = totalViewsScraper()
	instanceOne.writeExchangePageViewsCsv('exchangepageviews.csv')
	#instanceTwo.appendExchangePageViewsCsv('exchangepageviews.csv')
	instanceOne.plotExchangePageViews('exchangepageviews.csv')

	# Program must be run on different day sin order to gather data before it is
	# able to construct a meaningful plot.






