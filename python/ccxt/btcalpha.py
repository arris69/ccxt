# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import math
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import DDoSProtection


class btcalpha(Exchange):

    def describe(self):
        return self.deep_extend(super(btcalpha, self).describe(), {
            'id': 'btcalpha',
            'name': 'BTC-Alpha',
            'countries': ['US'],
            'version': 'v1',
            'has': {
                'fetchTicker': False,
                'fetchOHLCV': True,
                'fetchOrders': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'fetchMyTrades': True,
            },
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': 'D',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/42625213-dabaa5da-85cf-11e8-8f99-aa8f8f7699f0.jpg',
                'api': 'https://btc-alpha.com/api',
                'www': 'https://btc-alpha.com',
                'doc': 'https://btc-alpha.github.io/api-docs',
                'fees': 'https://btc-alpha.com/fees/',
                'referral': 'https://btc-alpha.com/?r=123788',
            },
            'api': {
                'public': {
                    'get': [
                        'currencies/',
                        'pairs/',
                        'orderbook/{pair_name}/',
                        'exchanges/',
                        'charts/{pair}/{type}/chart/',
                    ],
                },
                'private': {
                    'get': [
                        'wallets/',
                        'orders/own/',
                        'order/{id}/',
                        'exchanges/own/',
                        'deposits/',
                        'withdraws/',
                    ],
                    'post': [
                        'order/',
                        'order-cancel/',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.00135,
                        'LTC': 0.0035,
                        'XMR': 0.018,
                        'ZEC': 0.002,
                        'ETH': 0.01,
                        'ETC': 0.01,
                        'SIB': 1.5,
                        'CCRB': 4,
                        'PZM': 0.05,
                        'ITI': 0.05,
                        'DCY': 5,
                        'R': 5,
                        'ATB': 0.05,
                        'BRIA': 0.05,
                        'KZC': 0.05,
                        'HWC': 1,
                        'SPA': 1,
                        'SMS': 0.001,
                        'REC': 0.01,
                        'SUP': 1,
                        'BQ': 100,
                        'GDS': 0.1,
                        'EVN': 300,
                        'TRKC': 0.01,
                        'UNI': 1,
                        'STN': 1,
                        'BCH': None,
                        'QBIC': 0.5,
                    },
                },
            },
            'commonCurrencies': {
                'CBC': 'Cashbery',
            },
            'exceptions': {
                'exact': {},
                'broad': {
                    'Out of balance': InsufficientFunds,  # {"date":1570599531.4814300537,"error":"Out of balance -9.99243661 BTC"}
                },
            },
        })

    def fetch_markets(self, params={}):
        response = self.publicGetPairs(params)
        result = []
        for i in range(0, len(response)):
            market = response[i]
            id = self.safe_string(market, 'name')
            baseId = self.safe_string(market, 'currency1')
            quoteId = self.safe_string(market, 'currency2')
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': self.safe_integer(market, 'price_precision'),
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'active': True,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': self.safe_float(market, 'minimum_order_size'),
                        'max': self.safe_float(market, 'maximum_order_size'),
                    },
                    'price': {
                        'min': math.pow(10, -precision['price']),
                        'max': math.pow(10, precision['price']),
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                },
                'info': market,
                'baseId': None,
                'quoteId': None,
            })
        return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        request = {
            'pair_name': self.market_id(symbol),
        }
        if limit:
            request['limit_sell'] = limit
            request['limit_buy'] = limit
        response = self.publicGetOrderbookPairName(self.extend(request, params))
        return self.parse_order_book(response, None, 'buy', 'sell', 'price', 'amount')

    def parse_bids_asks(self, bidasks, priceKey=0, amountKey=1):
        result = []
        for i in range(0, len(bidasks)):
            bidask = bidasks[i]
            if bidask:
                result.append(self.parse_bid_ask(bidask, priceKey, amountKey))
        return result

    def parse_trade(self, trade, market=None):
        symbol = None
        if market is None:
            market = self.safe_value(self.marketsById, trade['pair'])
        if market is not None:
            symbol = market['symbol']
        timestamp = self.safe_timestamp(trade, 'timestamp')
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        cost = None
        if price is not None:
            if amount is not None:
                cost = float(self.cost_to_precision(symbol, price * amount))
        id = self.safe_string_2(trade, 'id', 'tid')
        side = self.safe_string_2(trade, 'my_side', 'side')
        orderId = self.safe_string(trade, 'o_id')
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': 'limit',
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        request = {}
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        if limit is not None:
            request['limit'] = limit
        trades = self.publicGetExchanges(self.extend(request, params))
        return self.parse_trades(trades, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='5m', since=None, limit=None):
        return [
            self.safe_timestamp(ohlcv, 'time'),
            self.safe_float(ohlcv, 'open'),
            self.safe_float(ohlcv, 'high'),
            self.safe_float(ohlcv, 'low'),
            self.safe_float(ohlcv, 'close'),
            self.safe_float(ohlcv, 'volume'),
        ]

    def fetch_ohlcv(self, symbol, timeframe='5m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'type': self.timeframes[timeframe],
        }
        if limit is not None:
            request['limit'] = limit
        if since is not None:
            request['since'] = int(since / 1000)
        response = self.publicGetChartsPairTypeChart(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetWallets(params)
        result = {'info': response}
        for i in range(0, len(response)):
            balance = response[i]
            currencyId = self.safe_string(balance, 'currency')
            code = self.safe_currency_code(currencyId)
            account = self.account()
            account['used'] = self.safe_float(balance, 'reserve')
            account['total'] = self.safe_float(balance, 'balance')
            result[code] = account
        return self.parse_balance(result)

    def parse_order_status(self, status):
        statuses = {
            '1': 'open',
            '2': 'canceled',
            '3': 'closed',
        }
        return self.safe_string(statuses, status, status)

    def parse_order(self, order, market=None):
        symbol = None
        if market is None:
            market = self.safe_value(self.marketsById, order['pair'])
        if market is not None:
            symbol = market['symbol']
        timestamp = self.safe_timestamp(order, 'date')
        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'amount')
        status = self.parse_order_status(self.safe_string(order, 'status'))
        id = self.safe_string_2(order, 'oid', 'id')
        trades = self.safe_value(order, 'trades', [])
        trades = self.parse_trades(trades, market)
        side = self.safe_string_2(order, 'my_side', 'type')
        filled = None
        numTrades = len(trades)
        if numTrades > 0:
            filled = 0.0
            for i in range(0, numTrades):
                filled = self.sum(filled, trades[i]['amount'])
        remaining = None
        if (amount is not None) and (amount > 0) and (filled is not None):
            remaining = max(0, amount - filled)
        return {
            'id': id,
            'clientOrderId': None,
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': None,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': trades,
            'fee': None,
            'info': order,
            'lastTradeTimestamp': None,
            'average': None,
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'type': side,
            'amount': amount,
            'price': self.price_to_precision(symbol, price),
        }
        response = self.privatePostOrder(self.extend(request, params))
        if not response['success']:
            raise InvalidOrder(self.id + ' ' + self.json(response))
        order = self.parse_order(response, market)
        amount = order['amount'] if (order['amount'] > 0) else amount
        return self.extend(order, {
            'amount': amount,
        })

    def cancel_order(self, id, symbol=None, params={}):
        request = {
            'order': id,
        }
        response = self.privatePostOrderCancel(self.extend(request, params))
        return response

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'id': id,
        }
        order = self.privateGetOrderId(self.extend(request, params))
        return self.parse_order(order)

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        if limit is not None:
            request['limit'] = limit
        orders = self.privateGetOrdersOwn(self.extend(request, params))
        return self.parse_orders(orders, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        request = {
            'status': '1',
        }
        return self.fetch_orders(symbol, since, limit, self.extend(request, params))

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        request = {
            'status': '3',
        }
        return self.fetch_orders(symbol, since, limit, self.extend(request, params))

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        if limit is not None:
            request['limit'] = limit
        trades = self.privateGetExchangesOwn(self.extend(request, params))
        return self.parse_trades(trades, None, since, limit)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        query = self.urlencode(self.keysort(self.omit(params, self.extract_params(path))))
        url = self.urls['api'] + '/'
        if path != 'charts/{pair}/{type}/chart/':
            url += 'v1/'
        url += self.implode_params(path, params)
        headers = {'Accept': 'application/json'}
        if api == 'public':
            if len(query):
                url += '?' + query
        else:
            self.check_required_credentials()
            payload = self.apiKey
            if method == 'POST':
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                body = query
                payload += body
            elif len(query):
                url += '?' + query
            headers['X-KEY'] = self.apiKey
            headers['X-SIGN'] = self.hmac(self.encode(payload), self.encode(self.secret))
            headers['X-NONCE'] = str(self.nonce())
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, code, reason, url, method, headers, body, response, requestHeaders, requestBody):
        if response is None:
            return  # fallback to default error handler
        #
        #     {"date":1570599531.4814300537,"error":"Out of balance -9.99243661 BTC"}
        #
        error = self.safe_string(response, 'error')
        feedback = self.id + ' ' + body
        if error is not None:
            self.throw_exactly_matched_exception(self.exceptions['exact'], error, feedback)
            self.throw_broadly_matched_exception(self.exceptions['broad'], error, feedback)
        if code == 401 or code == 403:
            raise AuthenticationError(feedback)
        elif code == 429:
            raise DDoSProtection(feedback)
        if code < 400:
            return
        raise ExchangeError(feedback)
