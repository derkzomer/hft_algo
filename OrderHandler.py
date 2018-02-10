from ApiHandler import order_api

class order(object):

	def record_order(self,price):
		return order_api().create_test_order('VENETH',100,price)