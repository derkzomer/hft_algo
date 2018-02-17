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
		# time_of_last_trade = db().time_of_last_trade()
		# time_since_last_trade = 

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
				
				trade_edge = r['average'] - cfg.trade_config['stdev'] * r['stdev']
				# trade_edge = 1
				
				print 'VENETH Trade Edge: ' + str(trade_edge)
				if self.veneth['veneth_delta'] < trade_edge:
					print "VENETH Recommendation: BUY"
					amount = float(cfg.trade_config['trade_amount']) / float(self.veneth['veneth_price'])

					db().record_validation(self.rules[0],"BUY",self.veneth['veneth_price'],"PENDING",validation_uuid)
					tracker_uuid = db().new_trade_tracker(self.veneth['veneth_price'],amount)
					db().new_trade(tracker_uuid,self.veneth['veneth_price'],amount,"BUY",cfg.trade_config['commission'])
				else:
					db().record_validation(self.rules[0],"HOLD",self.veneth['veneth_price'],"COMPLETE",validation_uuid)
					print 'VENETH Recommendation: HOLD'

	def trade_checks(self):

		tracker = db().get_active_trades()
		for tr in tracker:
			round = tr['round']

			purchase_commission_absolute = float(tr['commission']) * float(tr['purchase_price'])
			purchase_net_commission = float(tr['purchase_price']) + purchase_commission_absolute

			sale_commission_absolute = float(tr['commission']) * float(self.veneth['veneth_price'])
			sale_net_commission = float(self.veneth['veneth_price']) - sale_commission_absolute

			# purchase_net_commission = (float(tr['purchase_price']) * (1+tr['commission']))

			net = sale_net_commission - purchase_net_commission
			stop_loss_amount = cfg.trade_config['stop_loss_ratio'] * net
			print "stop_loss_amount: " + str(stop_loss_amount)

			print net

			if net > 0 or (round+1) == cfg.trade_config['rounds'] or net < stop_loss_amount:
				db().trade_validation(tr['uuid'],round+1,self.veneth['veneth_price'],tr['amount'],net,"SELL")
				db().conclude_trade_tracker(tr['uuid'],self.veneth['veneth_price'],net,round+1)
				db().new_trade(tr['uuid'],self.veneth['veneth_price'],tr['amount'],"SELL",cfg.trade_config['commission'])
			else:
				db().trade_validation(tr['uuid'],round+1,self.veneth['veneth_price'],tr['amount'],net,"HOLD")
				db().update_trade_tracker(tr['uuid'],self.veneth['veneth_price'],net,round+1)

crypto()