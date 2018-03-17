#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="QUINCE"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=1
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

#---------------------------------------------------
def trade(data):

    trades = []
    if data['type'] == 'book' and data['symbol'] == 'BOND':
        bids = data['buy']
        for price, size in bids:
            if price > 1000:
                trades.append(('SELL', 'BOND', price, size))

        asks = data['sell']
        for price, size in asks:
            if price < 1000:
                trades.append(('BUY', 'BOND', price, size))
    return trades

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    order = 0
    while True:
        data = read_from_exchange(exchange)
        print(1)
        print(data)
        if data!="":
            
            trades = trade(data)
            thistrade = trades[0]        
            dir,symbol,price,size = thistrade[0],thistrade[1],thistrade[2],thistrade[3]
            write_to_exchange(exchange, {"type": "add","order_id":order, "symbol":symbol,"dir":dir,"price":price,"size":size})
            ans_from_exchange = read_from_exchange(exchange)
            order +=1
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    
            print("The exchange replied:", ans_from_exchange, file=sys.stderr)
if __name__ == "__main__":
    main()
