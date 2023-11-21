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
# import telethon
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import os
# import re
import random
# from datetime import datetime
    
## =================================================================

load_dotenv()
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.

KAFKA_SERVER = os.getenv('KAFKA_SERVER',  'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

# Load Configurations:
MYNAME = f'GATHERER_{random.randint(1,1000)}'
with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]
logger.info(f"Following {channels_to_follow}")

## =================================================================

# Load Kafka producer
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, 
                        #  value_serializer=lambda v: pickle.dumps(v), 
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                         key_serializer=lambda v: str.encode(v) if v is not None else None)
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()
    
## =================================================================

# Run the gatherer
client = TelegramClient('Yashar', API_ID, API_KEY)
with client:
    #TODO: Make sure we are in all the channels we need to follow:
    
    # @client.on(events.Album(chats=channels_to_follow))#, function = produce)
    # async def albumHandler(event):
    #     logger.info(event)
    #     # event_type = 'newalbum'
    #     event = event.__dict__
        
    @client.on(events.NewMessage(incoming=True, chats=channels_to_follow))
    async def handleMsg(event):
        logger.info(event)
        # msg = event
        msg = {key:f'{value}' for key,value in event.message.__dict__.items()}
        producer.send(GATHERING_TOPIC, msg, key='MESSAGE')
        producer.flush()
        
    client.run_until_disconnected()

## =================================================================

producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})
