import telegram
from telegram.ext import Updater, Filters
import matplotlib
import matplotlib.pyplot as plt
import re
import io
from PIL import Image, ImageDraw, ImageFont
import random
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
        contract_name = i['symbol']
        break

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="<code>I'm a bot to help you trade BTC Move Options on Delta Exchange!</code>",parse_mode=telegram.ParseMode.HTML)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start, Filters.user(username="@username"))
dispatcher.add_handler(start_handler)

def info(update, context):
    product = delta_client.get_product(p_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text='<code>'+(product['description'])+'\nSymbol:'+(product['symbol'])+'\n\nSettlement Time:'+(product['settlement_time'])+'\nSTRIKE PRICE:'+(product['strike_price'])+'\n\nMaintenance Margin:'+(product['maintenance_margin'])+'\nContract Value:'+(product['contract_value'])+'\nContract Unit Currency:'+(product['contract_unit_currency'])+'\nMaker Commission Rate:'+(product['maker_commission_rate'])+'</code>', parse_mode=telegram.ParseMode.HTML)

from telegram.ext import CommandHandler
start_handler = CommandHandler('info', info, Filters.user(username="@username"))
dispatcher.add_handler(start_handler)

def position(update, context):
    position_details = delta_client.get_position(p_id)
    Premium = float(position_details['entry_price']) * abs(position_details['size']) * float(position_details['product']['contract_value'])
    context.bot.send_message(chat_id=update.effective_chat.id, text='<code>Size:'+str(position_details['size'])+'\nEntry Price:'+str(position_details['entry_price'])+'\nMargin:'+str(position_details['margin'])+'\nLiquidation Price:'+str(position_details['liquidation_price'])+'\nADL Level:'+str(position_details['adl_level'])+'\nAuto Top Up:'+str(position_details['auto_topup'])+'\nPremium:'+ str(Premium) +'</code>',parse_mode=telegram.ParseMode.HTML)

from telegram.ext import CommandHandler
start_handler = CommandHandler('position', position, Filters.user(username="@username"))
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
start_handler = CommandHandler('orderbook', orderbook, Filters.user(username="@username"))
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
                        if str(i['order_type'])=='market_order':
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) +  "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text="<code>\nOrder Type:"+ str(i['order_type']) + "\nLimit Price: " + str(i['limit_price']) + "\nSide: " + str(i['side'])+"\nSize: " + str(i['size']) + "\nUnfilled Size: " + str(i['unfilled_size']) + "</code>",parse_mode=telegram.ParseMode.HTML)



                j+=1


from telegram.ext import CommandHandler
start_handler = CommandHandler('orders', orders, Filters.user(username="@username"))
dispatcher.add_handler(start_handler)

def PNL(update, context):
    position_details = delta_client.get_position(p_id)
    depth = delta_client.get_L2_orders(p_id)

    #Buy/Sell and Contract Name
    font3= ImageFont.truetype('/fonts/Arial/ariblk.ttf', 35)
    if float(position_details['size'])>0:
        side = 'BUY'
    else:
        side = 'SELL'
    text3 = side + ' | ' + contract_name

    Premium = float(position_details['entry_price']) * abs(position_details['size']) * float(position_details['product']['contract_value'])
    Payoff = float(position_details['size']) * float(depth['mark_price']) * float(position_details['product']['contract_value'])
    Capital = float(position_details['entry_price']) - Premium

    if side == 'BUY':
        PNL = Payoff - Premium
    else:
        PNL = Payoff + Premium
        
    ROE = '%.2f' % ((PNL/Capital)*1000)


    if float(ROE)>0 and float(ROE)>25 and side=='BUY':
        image = Image.open(r'FULL PATH OF IMAGE DIRECTORY\templates\long.jpg')
    elif float(ROE)>30:
        image = Image.open(r'FULL PATH OF IMAGE DIRECTORY\templates\profit.jpg')
    elif float(ROE)<0 and abs(float(ROE))>20:
        image = Image.open(r'FULL PATH OF IMAGE DIRECTORY\templates\loss.jpg')
    else:
        image = Image.open(r'FULL PATH OF IMAGE DIRECTORY\templates\waiting.jpg')

    draw = ImageDraw.Draw(image)
    draw.text((100, 300), text3, font = font3, fill=(238,222,31), align ="center")

    font1 = ImageFont.truetype('/fonts/Arial/arialbd.ttf', 40)
    text1 = 'MY PNL/ROE'
    draw.text((100, 50), text1, font = font1, fill=(217,214,213), align ="center")

    #ROE% Text
    font2= ImageFont.truetype('/fonts/Arial/arialbd.ttf', 100)
    if float(ROE)>0:
        text2 = '+ ' + str(ROE) + ' %'
        draw.text((100, 150), text2, font = font2, fill=(9,231,46), align ="center")
    else:
        text2 = str(ROE) + ' %'
        draw.text((100, 150), text2, font = font2, fill=(254,13,1), align ="center")


    #Entry Price
    font4= ImageFont.truetype('/fonts/Arial/ariblk.ttf', 30)
    text4 = 'Entry Price\n' + str('%.2f' % float((position_details['entry_price'])))
    draw.text((700, 300), text4, font = font4, fill=(217,214,213), align ="center")

    #Random Text
    font5= ImageFont.truetype('/fonts/Arial/ariblk.ttf', 20)
    
    #More random texts can be added here. I will add more things related to BTC Volatility in next update.

    text5i = "The bollinger bands automatically widen\nwhen volatility increases and contract\nwhen volatility decreases"
    text5ii = "34.82% of Mondays are within -1% to 1% moves in BTC"
    text5iii = "Daily close, Weekly Close and CME contracts expiry\nare most of the times volatile"
    random_list = [text5i, text5ii]
    random_num = random.choice(random_list)
    text5 = str(random_num)
    draw.text((125, 600), text5, font = font5, fill=(212,212,212), align ="left")

    #Referral code
    font6= ImageFont.truetype('/fonts/Arial/arialbd.ttf', 25)
    text6 = 'REFERRAL CODE: ' + 'BLGNHE' #Replace with your REFERRAL CODE
    draw.text((550, 1000), text6, font = font6, fill=(147,189,184), align ="center")

    image = image.save('pnlimage.png')
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('pnlimage.png', 'rb'))

from telegram.ext import CommandHandler
start_handler = CommandHandler('PNL', PNL, Filters.user(username="@username"))
dispatcher.add_handler(start_handler)


updater.start_polling()
