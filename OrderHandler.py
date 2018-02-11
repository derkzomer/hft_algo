from ApiHandler import order_api
from DatabaseHandler import db

class order(object):

	def record_order(self,price,validation_uuid):
		# return order_api().create_test_order('VENETH',100,price)
		db().new_trade_tracker(validation_uuid,price,commission=0.001)