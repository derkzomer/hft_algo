from ApiHandler import order_api
from DatabaseHandler import db
import config as cfg

class order(object):

	def record_order(self,price,validation_uuid):
		# return order_api().create_test_order('VENETH',100,price)
		tracker_uuid = db().new_trade_tracker(price,commission=0.001)
		db().new_trade(tracker_uuid,price,"BUY",cfg.trade_config['commission'])