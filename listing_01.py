import time
import math
import json
import urllib
import hmac
import hashlib
import requests
import sqlite3
import logging
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen
class Binance():

    methods = {
            # public methods
            'ping':             {'url': 'api/v1/ping', 'method': 'GET', 'private': False},
            'time':             {'url': 'api/v1/time', 'method': 'GET', 'private': False},
            'exchangeInfo':     {'url': 'api/v1/exchangeInfo', 'method': 'GET', 'private': False},
            'depth':            {'url': 'api/v3/depth', 'method': 'GET', 'private': False},
            'avgPrice':         {'url': 'api/v3/avgPrice', 'method': 'GET', 'private': False},
            'price':            {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},
            'trades':           {'url': 'api/v1/trades', 'method': 'GET', 'private': False},
            'historicalTrades': {'url': 'api/v1/historicalTrades', 'method': 'GET', 'private': False},
            'aggTrades':        {'url': 'api/v1/aggTrades', 'method': 'GET', 'private': False},
            'klines':           {'url': 'api/v1/klines', 'method': 'GET', 'private': False},
            'ticker24hr':       {'url': 'api/v1/ticker/24hr', 'method': 'GET', 'private': False},
            'tickerPrice':      {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},
            'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
            # private methods
            'createOrder':      {'url': 'api/v3/order', 'method': 'POST', 'private': True},
            'testOrder':        {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
            'orderInfo':        {'url': 'api/v3/order', 'method': 'GET', 'private': True},
            'cancelOrder':      {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
            'openOrders':       {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
            'cancelAllOrders':  {'url': 'api/v3/openOrders', 'method': 'DELETE', 'private': True},
            'allOrders':        {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
            'account':          {'url': 'api/v3/account', 'method': 'GET', 'private': True},
            'myTrades':         {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
            'allCoins':         {'url': 'sapi/v1/capital/config/getall', 'method': 'GET', 'private': True},
            'accountSnapshot':  {'url': 'sapi/v1/accountSnapshot', 'method': 'GET', 'private': True},
            'systemStatus':     {'url': 'sapi/v1/system/status', 'method': 'GET', 'private': True},
            'accountStatus':    {'url': 'sapi/v1/account/status', 'method': 'GET', 'private': True},
            # wapi
            'depositAddress':   {'url': '/wapi/v3/depositAddress.html', 'method':'GET', 'private':True},
            'withdraw':   {'url': '/wapi/v3/withdraw.html', 'method':'POST', 'private':True},
            'depositHistory': {'url': '/wapi/v3/depositHistory.html', 'method':'GET', 'private':True},
            'withdrawHistory': {'url': '/wapi/v3/withdrawHistory.html', 'method':'GET', 'private':True},
            'withdrawFee': {'url': '/wapi/v3/withdrawFee.html', 'method':'GET', 'private':True},
            'accountStatus': {'url': '/wapi/v3/accountStatus.html', 'method':'GET', 'private':True},
            'systemStatus': {'url': '/wapi/v3/systemStatus.html', 'method':'GET', 'private':True},
    }
    
    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytearray(API_SECRET, encoding='utf-8')
        self.shift_seconds = 0

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            kwargs.update(command=name)
            return self.call_api(**kwargs)
        return wrapper

    def set_shift_seconds(self, seconds):
        self.shift_seconds = seconds
        
    def call_api(self, **kwargs):

        command = kwargs.pop('command')
        api_url = 'https://api.binance.com/' + self.methods[command]['url']

        payload = kwargs
        headers = {}
        
        payload_str = urllib.parse.urlencode(payload)
        if self.methods[command]['private']:
            payload.update({'timestamp': int(time.time() + self.shift_seconds - 1) * 1000})
            payload_str = urllib.parse.urlencode(payload).encode('utf-8')
            sign = hmac.new(
                key=self.API_SECRET,
                msg=payload_str,
                digestmod=hashlib.sha256
            ).hexdigest()

            payload_str = payload_str.decode("utf-8") + "&signature="+str(sign) 
            headers = {"X-MBX-APIKEY": self.API_KEY}

        if self.methods[command]['method'] == 'GET':
            api_url += '?' + payload_str

        response = requests.request(method=self.methods[command]['method'], url=api_url, data="" if self.methods[command]['method'] == 'GET' else payload_str, headers=headers)
        if 'code' in response.text:
            print(response.text)
        return response.json()
    
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#from binance_api import Binance
bot = Binance(
   API_KEY='512lRXSSKJl83vdD3BOKNxEku25H1ivpalzaniMVuRnquuXMwu5QAbUN6gCblzWm',
   API_SECRET='ijycHJoJP8ZY3D9SxNDoSTUORY9FlBXBIsbc6ZnAJ9SwhVVMcKsfESkGoGZvbTgX'
)

#простые функции=============================================================

def jsonWriteCoinList(coinListLen):
    print('#JSON coinListLen updated')
    cdt=datetime.now()
    fileName=str('coinListLenJournal/'+str(cdt.year)+'-'+str(cdt.month)+'-'+str(cdt.day)+'.txt')
    bJ=open(fileName,'a')
    newStroke=str(str(datetime.now()) + '\n' + str(coinListLen) + '\n\n')
    print(newStroke)
    bJ.write(newStroke)
    bJ.close()

while True:
    curTime=bot.time().get('serverTime')
    allCoins=bot.allCoins(curTime)
##    for i in range(len(allCoins)):
##        coinSymbol=allCoins[i].get("coin")
    ##    print(coinSymbol)
    jsonWriteCoinList(len(allCoins))
    time.sleep(1)




    
