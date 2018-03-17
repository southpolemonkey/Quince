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
test_mode = False 

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


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    vale_last_buy, vale_last_sell, valbz_last_buy, valbz_last_sell = \
        [None, None], [None, None ], [None, None], [None, None] 
    for i in range(20000):
        data = read_from_exchange(exchange)
        if data['type'] == 'ack' or data['type'] == 'reject':
            print(data)
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
        if data['type'] == 'book' and data['symbol'] == 'BOND':
            for j in data['sell']:
                if j[0] <= 1000:
                    put_order(exchange, 'BOND', 'BUY', j[0], j[1])
            for j in data['buy']:
                if j[0] >= 1000:
                    put_order(exchange, 'BOND', 'SELL', j[0], j[1])
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!


if __name__ == "__main__":
    main()
