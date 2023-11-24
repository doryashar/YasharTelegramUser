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
# from datetime import datetime
    
## =================================================================

load_dotenv()
API_ID_DOR  = os.getenv('API_ID_DOR', None) 
API_KEY_DOR = os.getenv('API_KEY_DOR', None)
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
                         value_serializer=lambda v: pickle.dumps(v), 
                        #  value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                         key_serializer=lambda v: str.encode(v) if v is not None else None)
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()
    
## =================================================================
"""
last_messages = []
async def brun():
    BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
    bot = TelegramClient('bot', API_ID_DOR, API_KEY_DOR)
    await bot.start()#bot_token=BOT_API_TOKEN)
    base_channel = 'https://t.me/YasharN3ws' #'2092038659' #bot.get_entity('https://t.me/YasharN3ws')
    if 1: #async def send_msg():
        while True:
            await asyncio.sleep(1)
            while len(last_messages):
                value = last_messages.pop()
                assert value.file is None == value.media is None, f"There's a media with no file or file with no media\nfile:{value.file}\nmedia:{value.media}"
                if value.file:
                    fd = io.BytesIO()
                    logger.info(f'found a file {value.file}')
                    value.download_media(file=fd)
                    logger.info(f'downloaded file into {fd.read()}')
                logger.info(f'Got message, sending {value}')
                await bot.send_message(base_channel, value)
    
    # bot.loop.run_until_complete(send_msg())

def crun():
    asyncio.run(brun())
    
import threading
threading.Thread(target=crun).start()
"""
## =================================================================
if 1:# async def arun():
    # Run the gatherer
    client = TelegramClient('Yashar', API_ID, API_KEY)
    with client: #async
        logger.info("Connected to telegram client")
        #TODO: Make sure we are in all the channels we need to follow:
        
        # @client.on(events.Album(chats=channels_to_follow))#, function = produce)
        # async def albumHandler(event):
        #     logger.info(event)
        #     # event_type = 'newalbum'
        #     event = event.__dict__
            
        @client.on(events.NewMessage(incoming=True, chats=channels_to_follow))
        async def handleMsg(event):
            msg = event.message
            
            smsg = {'file' : None}
            # smsg.update(event.message.to_dict())
            # logger.info(smsg)
            
            assert ((msg.file is None) == (msg.media is None)), f"There is {'no' if msg.media == None else ''}media with {'no' if msg.file == None else ''}file\nfile:{msg.file}\nmedia:{msg.media}"
            if msg.file:
                # fd = io.BytesIO()
                logger.info(f'found a file {msg.file.__dict__}')
                k = await msg.download_media(file=bytes) #was fd
                # logger.info(f'downloaded file into {k}')
                # logger.info(f'downloaded file into {fd.getbuffer()}')
                # downloaded file into fd.getvalue()
                smsg['file'] = k
                
            # msg._client = None
            
            # msg = {key:f'{value}' for key,value in event.message.__dict__.items()}
            
            tbytes= event.message._bytes()
            smsg['tbytes'] = tbytes
            
            producer.send(GATHERING_TOPIC, smsg, key='MESSAGE')
            producer.flush()
            
        client.run_until_disconnected() #await

# asyncio.run(arun())
## =================================================================

producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})
