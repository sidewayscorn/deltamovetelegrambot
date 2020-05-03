import telegram
from telegram.ext import Updater
import matplotlib
import matplotlib.pyplot as plt
import re
import io
from PIL import Image
updater = Updater(token='TELEGRAM BOT API TOKEN', use_context=True)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

from delta_rest_client import DeltaRestClient
import json



delta_client = DeltaRestClient(
    base_url='https://api.delta.exchange',
    api_key='DELTA API KEY',
    api_secret='DELTA API SECRET'
)


products = delta_client.get_all_products()

pattern = r'.*MV-BTC-D([^"]*)'
result = re.search(pattern, json.dumps(products, indent=2))

for i in json.loads(json.dumps(products)):
    if i['symbol'] == "MV-BTC-D"+ result.group(1):
        p_id=(i['id'])
        break

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="<code>I'm a bot to help you trade BTC Move Options on Delta Exchange!</code>",parse_mode=telegram.ParseMode.HTML)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def info(update, context):
    product = delta_client.get_product(p_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text='<code>'+(product['description'])+'\nSymbol:'+(product['symbol'])+'\n\nSettlement Time:'+(product['settlement_time'])+'\nSTRIKE PRICE:'+(product['strike_price'])+'\n\nMaintenance Margin:'+(product['maintenance_margin'])+'\nContract Value:'+(product['contract_value'])+'\nContract Unit Currency:'+(product['contract_unit_currency'])+'\nMaker Commission Rate:'+(product['maker_commission_rate'])+'</code>', parse_mode=telegram.ParseMode.HTML)

from telegram.ext import CommandHandler
start_handler = CommandHandler('info', info)
dispatcher.add_handler(start_handler)

def position(update, context):
    position_details = delta_client.get_position(p_id)
    Premium = float(position_details['entry_price']) * abs(position_details['size']) * float(position_details['product']['contract_value'])
    context.bot.send_message(chat_id=update.effective_chat.id, text='<code>Size:'+str(position_details['size'])+'\nEntry Price:'+(position_details['entry_price'])+'\nMargin:'+(position_details['margin'])+'\nLiquidation Price:'+(position_details['liquidation_price'])+'\nADL Level:'+str(position_details['adl_level'])+'\nAuto Top Up:'+str(position_details['auto_topup'])+'\nPremium:'+ Premium +'</code>',parse_mode=telegram.ParseMode.HTML)
    
from telegram.ext import CommandHandler
start_handler = CommandHandler('position', position)
dispatcher.add_handler(start_handler)

def orderbook(update, context):
    i=0     #Used as a counter for number of entries

    depth = delta_client.get_L2_orders(p_id)

    ask_tot=0.0
    ask_price =[]
    ask_quantity = []
    bid_price = []
    bid_quantity = []
    bid_tot = 0.0

    for ask in depth['sell_book']:
         if i<15:

            ask_price.append(float(ask['price']))
            ask_tot+=float(ask['size'])
            ask_quantity.append(ask_tot)

            i+=1


    j=0     #Secondary Counter for Bids


    for bid in depth['buy_book']:
        if j<15:
            bid_price.append(float(bid['price']))
            bid_tot += float(bid['size'])
            bid_quantity.append(bid_tot)

            j+=1



    fig, ax = plt.subplots()

    plt.plot(ask_price, ask_quantity, color = 'red', label='asks')
    plt.plot(bid_price, bid_quantity, color = 'green', label = 'bids')

    plt.legend()

    plt.savefig('obimage.png')

    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('obimage.png', 'rb'))


from telegram.ext import CommandHandler
start_handler = CommandHandler('orderbook', orderbook)
dispatcher.add_handler(start_handler)

def orders(update, context):
    orders = delta_client.get_orders()

    data = json.dumps(orders)
    data = json.loads(data)
    otype=[]

    j=0
    for i in data:
        if j<10:

            if i['product']['id'] == p_id:
                if (i['stop_price']!=None):
                    if (i['size']>i['unfilled_size']):
                        if str(i['order_type'])=='market_order':
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>Order Type: " + str(i['stop_order_type']) + "\nStop Price: " + str(i['stop_price']) +  "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "\nExecution Price: " + str(i['avg_fill_price']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>Order Type: " + str(i['stop_order_type']) + "\nStop Price: " + str(i['stop_price']) + "\nLimit Price: " + str(i['limit_price']) + "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "\nExecution Price: " + str(i['avg_fill_price']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        
                    else:
                        if str(i['order_type'])=='market_order':
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>Order Type: " + str(i['stop_order_type']) + "\nStop Price: " + str(i['stop_price']) +  "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>Order Type: " + str(i['stop_order_type']) + "\nStop Price: " + str(i['stop_price']) + "\nLimit Price: " + str(i['limit_price']) + "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)

                else:
                    if (i['size']>i['unfilled_size']):
                        if str(i['order_type'])=='market_order':
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) +  "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "\nExecution Price: " + str(i['avg_fill_price']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) + "\nLimit Price: " + str(i['limit_price']) + "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "\nExecution Price: " + str(i['avg_fill_price']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                            
                        
                    else:
                        if if str(i['order_type'])=='market_order':
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) +  "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) + "\nLimit Price: " + str(i['limit_price']) + "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                            
                        

                j+=1


from telegram.ext import CommandHandler
start_handler = CommandHandler('orders', orders)
dispatcher.add_handler(start_handler)



updater.start_polling()
