from ApiHandler import market_api
from DatabaseHandler import db

import time

class store(object):

	def __init__(self):

		self.pairs = [['BTCUSDT'],['VENBTC'],['TRXBTC'],['ETHBTC'],['CNDBTC'],['ETHUSDT'],['TRXETH'],['EOSBTC'],['BNBBTC'],['VENETH'],['ELFBTC'],['EOSETH'],['WTCBTC'],['ICXBTC'],['XRPBTC'],['VIBEBTC'],['CNDETH'],['NEOBTC'],['BNBUSDT'],['XVGBTC'],['NEOUSDT']]

		self.summary_prices = [time.time()]
		self.summary_headers = ["timestamp"]

		self.data = {}

		self.prices = self.query_prices()
		self.store_prices(self.prices)

	def query_prices(self):
		return market_api().get_all_prices()

	def store_prices(self,prices):
		for d in prices:
			for p in self.pairs:
				if (d['symbol'] in p):
					self.summary_headers.append(d['symbol'])
					self.summary_prices.append(d['price'])

					self.data[d['symbol']] = {"price":d['price'],"timestamp":time.time(),"pair":d['symbol']}

		db().insert_new_price([self.data],'binance')
