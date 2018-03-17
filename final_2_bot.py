#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
from random import randint

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="Quince"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True 

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def put_order(exchange, symb, dir, price, size):
    write_to_exchange(exchange, {"type": "add",
                     "order_id": randint(1, 2**32),
                     "symbol": symb,
                     "dir": dir,
                     "price": price,
                     "size": size})
    print('order sent!')

def ema(alpha, new, last=None):
    if last == None:
        return new
    else:
        return alpha * new + (1 - alpha) * last


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    vale_last_buy, vale_last_sell, valbz_last_buy, valbz_last_sell = \
        [None, None], [None, None ], [None, None], [None, None]

    gs_last_buy, gs_last_sell = [None, None], [None, None]
    gs_last = None
    alpha = 0.3
    gs_count = 0
    diff = 0.1

    for i in range(20000):
        data = read_from_exchange(exchange)
        if data['type'] == 'ack' or data['type'] == 'reject':
            print(data)
        '''
        ## pair trading 
        if data['type'] == 'book' and data['symbol'] == 'VALE':
            try:
                vale_last_sell = data['sell']
                vale_last_buy = data['buy']
            except:
                pass
        if data['type'] == 'book' and data['symbol'] == 'VALBZ':
            try:
                valbz_last_sell = data['sell']
                valbz_last_buy = data['buy']
            except:
                pass
            try:
                if vale_last_buy[0][0] >= valbz_last_sell[0][0]:
                    put_order(exchange, 'VALBZ', 'BUY', valbz_last_sell[0][0], vale_last_sell[0][1])
                    put_order(exchange, 'VALE', 'SELL', vale_last_buy[0][0], vale_last_sell[0][1])
            except:
                    pass
            try:
                if vale_last_sell[0][0] <= valbz_last_buy[0][0]:
                    put_order(exchange, 'VALE', 'BUY', valbz_last_sell[0][0], vale_last_buy[0][1])
                    put_order(exchange, 'VALBZ', 'SELL', vale_last_buy[0][0], vale_last_buy[0][1])
            except:
                    pass
        ## trading bond
        if data['type'] == 'book' and data['symbol'] == 'BOND':
            for j in data['sell']:
                if j[0] <= 1000:
                    put_order(exchange, 'BOND', 'BUY', j[0], j[1])
            for j in data['buy']:
                if j[0] >= 1000:
                    put_order(exchange, 'BOND', 'SELL', j[0], j[1])
        '''
        ## EMA trading for Goldman Sachs
        if data['type'] == 'book' and data['symbol'] == 'GS':
            try:
                gs_last_sell = data['sell']
                gs_last_buy = date['buy']
                gs_new = (gs_last_buy + gs_last_sell) / 2
                last = ema(0.3,gs_new,gs_last)
            except:
                pass
            try:
                if diff * (last - gs_new) > 0:
                    gs_count += 1
                else:
                    gs_count = 0
                diff = last - gs_new
                if gs_count >= 5:
                    if diff > 0:
                        put_order(exchange, 'GS', 'BUY', gs_last_sell[0][0])
                    else:
                        put_order(exchange, 'GS', 'SELL', gs_last_buy[0][0])
                    #put_order(exchange, 'GS', 'BUY', gs_last_sell[0][0])
                    #put_order(exchange, 'GS', 'SELL', gs_last_buy[0][0])
            except:
                pass
            #last = ema(0.2, gs_new, gs_last)


if __name__ == "__main__":
    main()
