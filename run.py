from TradeRulesHandler import trade_rules
from PriceStorageHandler import store
from DatabaseHandler import db
from OrderHandler import order
from ApiHandler import market_api
from ApiHandler import order_api
from ApiHandler import account_api

import json

class crypto(object):

	def __init__(self):
		self.rules = self.get_trade_rules()
		self.rule = json.loads(self.rules[2])
		self.get_price()
		store()

	def get_trade_rules(self):
		return trade_rules().check_rules()

	def get_price(self):
		veneth_price = market_api().get_latest_trades('VENETH')[0]['price']
		veneth_old_price = db().calculate_price_change('VENETH','binance')

		self.veneth = {
			'veneth_price':veneth_price,
			'veneth_old_price':veneth_old_price,
			'veneth_delta':1-(float(veneth_price)/float(veneth_old_price))
		}

		btcusdt_price = market_api().get_latest_trades('BTCUSDT')[0]['price']
		btcusdt_old_price = db().calculate_price_change('BTCUSDT','binance')
		self.btcusdt = {
			'btcusd_price':btcusdt_price,
			'btcusd_old_price':btcusdt_old_price,
			'btcusdt_delta':1-(float(btcusdt_price)/float(btcusdt_old_price))
		}

		self.validate()

	def validate(self):
		print self.veneth
		print self.btcusdt
		min = self.rule['summary']['min']
		max = self.rule['summary']['max']
		gran = self.rule['summary']['granularity']
		p = 0
		for i in [float(j) / 1000 for j in range(int(min*1000)-int(gran*1000), int(max*1000), int(gran*1000))]:
			if self.btcusdt['btcusdt_delta'] > i and self.btcusdt['btcusdt_delta'] <= i+gran:
				p = i

		print "BTCUSDT Group: " + str(p) + ' to ' + str(p+gran)
		for r in self.rule['rules']:
			if p == r['low']:
				print 'Expected VENETH change: ' + str(r['average'])
				# print 'expected standard deviation: ' + str(r['stdev'])
				trade_edge = r['average'] - 1.25 * r['stdev']
				print 'VENETH Trade Edge: ' + str(trade_edge)
				if self.veneth['veneth_delta'] < trade_edge:
					print "VENETH Recommendation: BUY"
					db().record_validation(self.rules[0],"BUY",self.veneth['veneth_price'],"PENDING")
					print order().record_order(self.veneth['veneth_price'])
				else:
					db().record_validation(self.rules[0],"HOLD",self.veneth['veneth_price'],"COMPLETE")
					print 'VENETH Recommendation: HOLD'
		



crypto()