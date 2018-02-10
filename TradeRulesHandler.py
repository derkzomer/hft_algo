from DatabaseHandler import db

class trade_rules(object):

	def check_rules(self):
		return db().get_trade_rule('VENETH')
		