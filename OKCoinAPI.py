'''author:lazyp
   email :lazy_p@163.com
   date  :2014-06-11
'''
#-*- coding:utf-8 -*-
import hashlib
import urllib
import httplib
import json
import time

class OKCoinAPI:
        __DOMAIN__  = "www.okcoin.com"
        __OKCOIN_TICKER_API__ = "https://www.okcoin.com/api/ticker.do?symbol=btc_cny"
        __OKCOIN_TRADE_API__  = "https://www.okcoin.cn/api/trades.do"
        __OKCOIN_KLINE_API__  = "https://www.okcoin.com/kline/period.do?step=%d&symbol=okcoinbtccny"
        __HEADERS__ = {"Content-type" : "application/x-www-form-urlencoded"}

        def __init__(self , partner , secretkey):
                self.partner = partner
                self.secretkey = secretkey
                self.pre_call_time = time.mktime(time.localtime())

        def __append_signature__(self , params):
                reqBody = ""
                for k in sorted(params.keys()):
                        if len(reqBody) > 0:
                                reqBody += "&"
                        reqBody += (k + "=" + str(params[k]))
         #       print reqBody
                sign = hashlib.new("md5" , reqBody+self.secretkey).hexdigest().upper()
                reqBody += ("&sign="+sign)
                return reqBody

        def __rpc_call__(self , reqUri , params):
                reqBody = self.__append_signature__(params)
        #       print reqBody
                curtime = time.mktime(time.localtime())
                if curtime - self.pre_call_time < 2:
                    time.sleep(2)
                self.pre_call_time = curtime
                
                ret = "" 
                http = httplib.HTTPSConnection(self.__DOMAIN__)
                http.request("POST" , reqUri , reqBody , self.__HEADERS__)
                resp = http.getresponse()
                if resp.status != 500:
                        ret = resp.read()
                http.close() 
                return ret

        def getUserInfo(self):
                params = dict({"partner" : self.partner})
                return self.__rpc_call__("/api/userinfo.do" , params)

        def getOrders(self , order_id , symbol):
                params= dict({"partner":self.partner , "order_id":order_id , "symbol":symbol})
                return self.__rpc_call__("/api/getorder.do" , params)

        def trade(self , symbol , type , rate , amount):
                params= dict({"partner":self.partner , "symbol":symbol , "type" :  type})
                if type == "buy_market":
                        params["rate"] = rate
                elif type == "sell_market":
                        params["amount"] = amount
                else:
                        params["rate"] = rate
                        params["amount"] = amount
                return self.__rpc_call__("/api/trade.do" , params)

        def sell(self , symbol , rate , amount):
                if symbol is None or rate is None or amount is None:
                        raise Exception ("The symbol , rate ,amount all can't None" , "")
                return self.trade(symbol , "sell" , rate , amount)

        def buy(self , symbol , rate , amount):
                if symbol is None or rate is None or amount is None:
                        raise Exception ("The symbol , rate ,amount all can't None" , "")
                return self.trade(symbol , "buy" , rate , amount)

        def cancelorder(self , order_id , symbol):
                if order_id <= 0:
                        raise Exception("order_id" , "greater than 0")

                params= dict({"partner":self.partner , "order_id":order_id , "symbol":symbol})
                return self.__rpc_call__("/api/cancelorder.do" , params)

        def getticker(self):
                http = urllib.urlopen(self.__OKCOIN_TICKER_API__)
                content = http.read()
                ticker = json.loads(content)['ticker']
                return ticker

        def gethistorytrades(self , since):
            __url = self.__OKCOIN_TRADE_API__
            if since is not None:
                __url = __url + "?since="+since
            http = urllib.urlopen(__url)
            content = http.read()
            trades = json.loads(content)
            return trades

        def getklinedata(self , step):
            __url = self.__OKCOIN_KLINE_API__ % step
            http = urllib.urlopen(__url)
            content = http.read()
            return content


