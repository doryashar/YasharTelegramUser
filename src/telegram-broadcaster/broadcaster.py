#!/usr/bin/env python

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

## =================================================================

# Main
# import copy
import json
import dill as pickle
import asyncio
# import telethon
from telethon import TelegramClient, events #, sync
from dotenv import load_dotenv
import os
import random
    
## =================================================================
load_dotenv()
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

KAFKA_SERVER = os.getenv('KAFKA_SERVER',  'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

# Load Configurations:
MYNAME = f'BROADCASTER_{random.randint(1,1000)}'
# Load Configurations:
#TODO:

## =================================================================

# Load Kafka producer
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, 
                        #  value_serializer=lambda v: pickle.dumps(v), 
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                         key_serializer=lambda v: str.encode(v) if v is not None else None)
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()

# Load Kafka Consumer
from kafka import KafkaConsumer
consumer = KafkaConsumer(PRODUCE_TOPIC, bootstrap_servers=KAFKA_SERVER,
                        #  value_deserializer = lambda v: pickle.loads(v),
                         value_deserializer = lambda v: json.loads(v.decode('utf-8')),
                         ) #, group_id='my_favorite_group')
# consumer.assign([TopicPartition('foobar', 2)]) # Manually assign partition list
# consumer.subscribe(['msgpackfoo'])

## =================================================================

    
bot = TelegramClient('bot', API_ID, API_KEY).start(bot_token=BOT_API_TOKEN)

# dor = bot.get_entity('dorito123')
base_channel = 'https://t.me/YasharN3ws' #'2092038659' #bot.get_entity('https://t.me/YasharN3ws')

logger.info("Start listening to MESSAGES")
for msg in consumer:
    logger.info(msg)
    value = msg.value
    # bot.loop.run_until_complete(bot.send_message(base_channel, value))
    bot.loop.run_until_complete(bot.send_message(base_channel, value.get('message', 'UnKNOWN')))
    
# metrics = consumer.metrics()
# print(metrics)

## =================================================================

producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})



# @bot.on(events.NewMessage(pattern='/start'))
# async def start(event):
#     """Send a message when the command /start is issued."""
#     await event.respond('Hi!')
#     raise events.StopPropagation

# @bot.on(events.NewMessage)
# async def echo(event):
#     """Echo the user message."""
#     await event.respond(event.text)

# def main():
#     """Start the bot."""
    # bot.run_until_disconnected()

# if __name__ == '__main__':
#     main()