import MySQLdb
import time
import config as cfg
import uuid
import itertools

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

	def get_active_trade_count(self):
		query = 'SELECT COUNT(*) FROM TradeTracker WHERE trade_status = "PENDING"'
		self.cur.execute(query)
		for row in self.cur.fetchall():
			return row[0]

	def get_active_trades(self):
		query = 'SELECT * FROM TradeTracker WHERE trade_status = "PENDING"'
		self.cur.execute(query)
		desc = self.cur.description
		column_names = [col[0] for col in desc]
		data = [dict(itertools.izip(column_names, row)) for row in self.cur.fetchall()]

		return data

	def insert_new_price(self,data,exchange):
		for d in data:
			for key, value in d.iteritems():
				previous_price = float(self.calculate_price_change(value["pair"],exchange))
				result = self.cur.execute("INSERT INTO LastPrice (_ts,price,pair,exchange,previous_price) VALUES (%s,%s,%s,%s,%s);",(str(value["timestamp"]),str(value["price"]),value["pair"],exchange,previous_price))
				self.db.commit()

	def record_validation(self,trade_rule_uuid,decision,purchase_price,status,uuid):
		result = self.cur.execute("INSERT INTO RuleValidations (uuid,_ts,trade_rule_uuid,decision,purchase_price,status) VALUES (%s,%s,%s,%s,%s,%s);",(uuid,str(time.time()),trade_rule_uuid,decision,purchase_price,status))
		self.db.commit()

	def new_trade_tracker(self,validation_uuid,price,commission):
		tracker_uuid = uuid.uuid4()
		result = self.cur.execute("INSERT INTO TradeTracker (uuid,validation_uuid,round,purchase_price,commission) VALUES (%s,%s,%s,%s,%s);",(tracker_uuid,validation_uuid,0,price,commission))
		self.db.commit()

	def update_trade_tracker(self,validation_uuid,price,net,round):
		self.cur.execute('UPDATE TradeTracker SET round_{r}_price = {p}, round_{r}_net = {n}, round = {r} WHERE validation_uuid = "{v}"'.format(v=validation_uuid, r=round, p=price, n=net))
		self.db.commit()

	def conclude_trade_tracker(self,validation_uuid,price,net,round):
		self.cur.execute('UPDATE TradeTracker SET round_{r}_price = {p}, round_{r}_net = {n}, round = {r}, trade_net = {n}, trade_status = "COMPLETE" WHERE validation_uuid = "{v}"'.format(v=validation_uuid, r=round, p=price, n=net))
		self.db.commit()

	def calculate_price_change(self,pair,exchange):
		# print 'SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange)
		self.cur.execute('SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange))
		return self.cur.fetchone()[0]

	def close(self):
		self.db.close()

# db().get_trade_rule('VENETH')