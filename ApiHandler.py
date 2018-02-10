from binance.client import Client
from binance.enums import *
import config as cfg

class market_api(object):

	def __init__(self):
		self.client = Client(cfg.api_keys['key'],cfg.api_keys['secret'], {"verify": True, "timeout": 20})

	def get_all_orders(self,symbol='VENETH'):
		return self.client.get_all_orders(symbol=symbol, requests_params={'timeout': 5})

	def ping(self):
		return self.client.ping()

	def get_system_status(self):
		return self.client.get_system_status()

	def get_exchange_info(self):
		return self.client.get_exchange_info()

	def get_symbol_info(self,symbol='VENETH'):
		return self.client.get_symbol_info(symbol=symbol)

	def get_market_depth(self,symbol='VENETH'):
		return self.client.get_order_book(symbol=symbol)

	def get_latest_trades(self,symbol):
		return self.client.get_recent_trades(symbol=symbol)

	def get_historical_trades(self,symbol='VENETH'):
		return self.client.get_historical_trades(symbol=symbol)

	def get_aggregate_trades(self,symbol='VENETH'):
		return self.client.get_aggregate_trades(symbol=symbol)

	def get_tickers(self):
		return self.client.get_ticker()

	def get_all_prices(self):
		return self.client.get_all_tickers()

	def get_orderbook_tickers(self):
		return self.client.get_orderbook_tickers()

class order_api(object):

	def __init__(self):
		self.client = Client("KCl8UvtnFcrlEgpqiwJlA0dr2SM3DuhKHHxiRtHA8oe7yl0JZYqas8oN2XNK0Lfz", "2wj46v8IAKpXoeigAmzfPg1VEjYi3oItNTeeNcEkDrK1HIev4nZHJr1Cd8tiJ5L0", {"verify": True, "timeout": 20})

	def get_all_orders(self,symbol='VENETH',limit=10):
		return self.get_all_orders(symbol,limit)

	# def create_order(self, symbol='VENETH', side='BUY', type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC, quantity=100, price='0.00001'):
		# self.client.create_order(symbol,side,type,timeInForce,quantity,price)

	# def create_sell_limit_order(self):
		# self.order = client.order_limit_buy(symbol,quantity,price)

	# def create_market_order(self):
		# pass

	def create_test_order(self,symbol,quantity,price):
		return self.client.create_test_order(symbol=symbol,quantity=quantity,price=price,side='BUY',type='LIMIT',timeInForce='GTC')

	def get_all_orders(self,symbol='VENETH'):
		return self.client.get_all_orders(symbol=symbol)

	def get_open_orders(self,symbol='VENETH'):
		return self.client.get_open_orders(symbol=symbol)

	def cancel_order(self,symbol='VENETH',orderId=0):
		return self.client.cancel_order(symbol=symbol,orderId=orderId)

	def order_status(self,symbol='VENETH',orderId=0):
		return self.client.get_order(symbol=symbol,orderId=orderId)

class account_api(object):

	def __init__(self):
		self.client = Client("KCl8UvtnFcrlEgpqiwJlA0dr2SM3DuhKHHxiRtHA8oe7yl0JZYqas8oN2XNK0Lfz", "2wj46v8IAKpXoeigAmzfPg1VEjYi3oItNTeeNcEkDrK1HIev4nZHJr1Cd8tiJ5L0", {"verify": True, "timeout": 20})

	def get_account_info(self):
		return self.client.get_account()

	def get_account_balance(self,asset='BTC'):
		return self.client.get_asset_balance(asset=asset)

	def get_account_status(self):
		return self.client.get_account_status()

	def get_trades(self,symbol='VENETH'):
		return self.client.get_my_trades(symbol=symbol)