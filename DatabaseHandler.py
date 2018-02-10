import MySQLdb
import uuid
import time
import config as cfg

class db(object):

	def __init__(self):
		self.db = MySQLdb.connect(host=cfg.db_config['host'],
		                     user=cfg.db_config['user'],
		                     passwd=cfg.db_config['passwd'],
		                     db=cfg.db_config['db'])

		self.cur = self.db.cursor()

	def get_trade_rule(self,pair):
		query = 'SELECT * FROM TradeRules WHERE pair = "{}"'.format(pair)
		self.cur.execute(query)
		for row in self.cur.fetchall():
			return row

	def insert_new_price(self,data,exchange):
		for d in data:
			for key, value in d.iteritems():
				previous_price = float(self.calculate_price_change(value["pair"],exchange))
				result = self.cur.execute("INSERT INTO LastPrice (_ts,price,pair,exchange,previous_price) VALUES (%s,%s,%s,%s,%s);",(str(value["timestamp"]),str(value["price"]),value["pair"],exchange,previous_price))
				self.db.commit()

	def record_validation(self,trade_rule_uuid,decision,purchase_price,status):
		u = uuid.uuid4()
		result = self.cur.execute("INSERT INTO RuleValidations (uuid,_ts,trade_rule_uuid,decision,purchase_price,status) VALUES (%s,%s,%s,%s,%s,%s);",(u,str(time.time()),trade_rule_uuid,decision,purchase_price,status))
		self.db.commit()

	def calculate_price_change(self,pair,exchange):
		# print 'SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange)
		self.cur.execute('SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange))
		return self.cur.fetchone()[0]

	def close(self):
		self.db.close()

# db().get_trade_rule('VENETH')