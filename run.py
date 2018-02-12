from TradeRulesHandler import trade_rules
from PriceStorageHandler import store
from DatabaseHandler import db
from OrderHandler import order
from ApiHandler import market_api
from ApiHandler import order_api
from ApiHandler import account_api

import config as cfg
import json
import uuid

class crypto(object):

	def __init__(self):
		active_trades = db().get_active_trade_count();
		concurrent_trades = cfg.trade_config['concurrent_trades']

		self.get_price()

		self.trade_checks()

		if active_trades < concurrent_trades:
			self.rules = self.get_trade_rules()
			self.rule = json.loads(self.rules[2])
			self.validate()
		
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

	def validate(self):

		validation_uuid = uuid.uuid4()

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
				
				trade_edge = r['average'] - 1.5 * r['stdev']
				# trade_edge = 1
				
				print 'VENETH Trade Edge: ' + str(trade_edge)
				if self.veneth['veneth_delta'] < trade_edge:
					print "VENETH Recommendation: BUY"
					db().record_validation(self.rules[0],"BUY",self.veneth['veneth_price'],"PENDING",validation_uuid)
					order().record_order(self.veneth['veneth_price'],validation_uuid)
				else:
					db().record_validation(self.rules[0],"HOLD",self.veneth['veneth_price'],"COMPLETE",validation_uuid)
					print 'VENETH Recommendation: HOLD'

	def trade_checks(self):

		trades = db().get_active_trades()
		for trade in trades:
			print trade
			validation_uuid = trade['validation_uuid']
			round = trade['round']
			if round == 0:
				last_price = trade['purchase_price']
			else:
				last_price = trade['round_'+str(round)+'_price']

			purchase_net_commission = (float(trade['purchase_price']) * (1+trade['commission']))
			print purchase_net_commission
			print float(self.veneth['veneth_price'])
			net = (float(self.veneth['veneth_price']) / purchase_net_commission)-1
			print net

			if net > 0 or (round+1) == 5:
				db().conclude_trade_tracker(validation_uuid,self.veneth['veneth_price'],net,round+1)
			else:
				db().update_trade_tracker(validation_uuid,self.veneth['veneth_price'],net,round+1)

crypto()