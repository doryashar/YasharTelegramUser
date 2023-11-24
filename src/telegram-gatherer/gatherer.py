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
import io
import asyncio
# import telethon
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import os
# import re
import random
import gatherer_funcs
# from datetime import datetime
    
## =================================================================
# Load Configurations:

load_dotenv()
API_ID_DOR  = os.getenv('API_ID_DOR', None) 
API_KEY_DOR = os.getenv('API_KEY_DOR', None)
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.

KAFKA_SERVER = os.getenv('KAFKA_SERVER',  'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

MYNAME = f'GATHERER_{random.randint(1,1000)}'
with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]
logger.info(f"Following {channels_to_follow}")

#TODO: Fix config module
with open('db/config.json', 'r') as fd:
    cfg = json.load(fd)
    
## =================================================================

# Load Kafka producer
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, 
                         value_serializer=lambda v: pickle.dumps(v), 
                        #  value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                         key_serializer=lambda v: str.encode(v) if v is not None else None)
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()

## =================================================================

async def run():
    # Run the gatherer
    client = TelegramClient('Yashar', API_ID, API_KEY)
    with client: #async
        logger.info("Connected to telegram client")
        
        # Make sure we are in all the channels we need to follow:
        gatherer_funcs.join_channels(client, channels_to_follow)
        
        #TODO: add album handling
        # @client.on(events.Album(chats=channels_to_follow))#, function = produce)
        # async def albumHandler(event):
        #     logger.info(event)
        #     # event_type = 'newalbum'
        #     event = event.__dict__
            
        @client.on(events.NewMessage(incoming=True, chats=channels_to_follow))
        async def handleMsg(event):
            msg = event.message
            smsg = {'file' : None}
            
            # Handle files
            assert ((msg.file is None) == (msg.media is None)), f"There is {'no' if msg.media == None else ''}media with {'no' if msg.file == None else ''}file\nfile:{msg.file}\nmedia:{msg.media}"
            if msg.file:
                # fd = io.BytesIO()
                logger.info(f'found a file {msg.file.__dict__}')
                media = await msg.download_media(file=bytes) #was fd-> downloaded file into fd.getvalue()
                smsg['file'] = media
            
            # Prepare the object for transmission
            # msg._client = None
            tbytes= event.message._bytes()
            smsg['tbytes'] = tbytes
            
            logger.info(f'Sending msg')
            producer.send(GATHERING_TOPIC, smsg, key='MESSAGE')
            producer.flush()
            
        client.run_until_disconnected() #await

asyncio.run(run())
## =================================================================

producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})
