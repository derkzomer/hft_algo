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

	def get_tracker_trades(self,uuid):
		query = 'SELECT * FROM Trades WHERE validation_uuid = "{}"'.format(uuid)
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

	def new_trade_tracker(self,price,amount):
		tracker_uuid = uuid.uuid4()
		commission = cfg.trade_config['commission']
		result = self.cur.execute("INSERT INTO TradeTracker (uuid,round,purchase_price,amount,commission) VALUES (%s,%s,%s,%s,%s);",(tracker_uuid,0,price,amount,commission))
		self.db.commit()
		return tracker_uuid

	def update_trade_tracker(self,tracker_uuid,price,net,round):
		self.cur.execute('UPDATE TradeTracker SET round = {r} WHERE uuid = "{t}"'.format(t=tracker_uuid, r=round))
		self.db.commit()

	def conclude_trade_tracker(self,tracker_uuid,price,net,round):
		self.cur.execute('UPDATE TradeTracker SET round = {r}, trade_net = {n}, trade_status = "COMPLETE" WHERE uuid = "{t}"'.format(t=tracker_uuid, r=round, n=net))
		self.db.commit()

	def trade_validation(self,trade_tracker_uuid,round,amount,price,net,status):
		validation_uuid = uuid.uuid4()
		self.cur.execute("INSERT INTO PotentialTrades (uuid,trade_tracker_uuid,round,amount,price,net,status) VALUES (%s,%s,%s,%s,%s,%s,%s);",(validation_uuid,trade_tracker_uuid,round,amount,price,net,status))
		self.db.commit()

	def select_last_round(self,trade_tracker_uuid):
		query = 'SELECT * FROM PotentialTrades WHERE trade_tracker_uuid = "{}" ORDER BY round DESC LIMIT 1'.format(uuid)
		self.cur.execute(query)
		desc = self.cur.description
		column_names = [col[0] for col in desc]
		data = [dict(itertools.izip(column_names, row)) for row in self.cur.fetchall()]

		return data

	def new_trade(self,trade_tracker_uuid,price,amount,type,commission):
		trade_uuid = uuid.uuid4()
		self.cur.execute("INSERT INTO Trades (uuid,trade_tracker_uuid,price,amount,type,commission) VALUES (%s,%s,%s,%s,%s,%s);",(trade_uuid,trade_tracker_uuid,price,amount,type,commission))
		self.db.commit()

	def calculate_price_change(self,pair,exchange):
		# print 'SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange)
		self.cur.execute('SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange))
		return self.cur.fetchone()[0]

	def time_of_last_trade(self):
		# print 'SELECT price FROM LastPrice WHERE id = ( SELECT max(id) FROM LastPrice WHERE 1=1 AND pair = "{p}" AND exchange = "{e}") AND pair = "{p}" AND exchange = "{e}";'.format(p=pair, e=exchange)
		self.cur.execute('SELECT max(created_at) FROM TradeTracker')
		return self.cur.fetchone()[0]		

	def close(self):
		self.db.close()

# db().get_trade_rule('VENETH')