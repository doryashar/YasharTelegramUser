#!/usr/bin/env python

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info(f'Got logger {__name__}')

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
import importlib

# importlib.import_module('telegram_gatherer.gatherer_funcs', package=__package__)

from .gatherer_funcs import join_channels, parse_telegram_msg
# from datetime import datetime
    
## =================================================================
# Load Configurations:

load_dotenv()
API_ID  = os.getenv('API_ID') 
API_KEY = os.getenv('API_KEY')  # api_hash from https://my.telegram.org, under API Development.

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

MYNAME = f'GATHERER_{random.randint(1,1000)}'
base_channel = os.getenv('BASE_CHANNEL', 'YasharN3WS')
with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]
logger.info(f"Following {channels_to_follow}")

#TODO: Fix config module
with open('db/config.json', 'r') as fd:
    cfg = json.load(fd)


## =================================================================
try:
    # Load Kafka producer
    from kafka import KafkaProducer
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], 
                            client_id=MYNAME, 
                            value_serializer=lambda v: pickle.dumps(v), 
                            #  value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                            key_serializer=lambda v: str.encode(v) if v is not None else None)
    producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
    producer.flush()
except Exception as e:
    logger.error(f'Failed to load Kafka: {e}')
    if cfg.get('allow_no_kafka', False):
        class dummyProducer: 
            def flush(self, *args, **kwargs): pass
            def send(self, *args, **kwargs): pass
        producer = dummyProducer()
    else :
        raise
    

## =================================================================

global last_ten_msgs
last_ten_msgs = []

async def send_event(msg):
    smsg = {'media' : None}
    
    # Handle files
    if msg.file:
        # fd = io.BytesIO()
        global last_ten_msgs
        last_ten_msgs = last_ten_msgs[:10] + [msg]
        logger.info(f'found a file {msg.file.__dict__}')
        media = await msg.download_media(file=bytes) #was fd-> downloaded file into fd.getvalue()
        smsg['media'] = media
    
    # Prepare the object for transmission
    # msg._client = None
    # if try:
    #     pickle.dumps(msg)
    # except Exception:
    #     logger.error('error')
        
    # msg.client = None
    # msg._abc_impl = None
    
    # logger.info(f'Sending msg\n{msg}')
    
    # msg = msg._bytes()
    smsg['msg'] = msg
    return smsg

## =================================================================
    
async def run():
    # Run the gatherer
    client = TelegramClient('Yashar', API_ID, API_KEY)
    async with client:
        logger.info("Connected to telegram client")
        
        # Make sure we are in all the channels we need to follow:
        await join_channels(client, channels_to_follow)
        base_channel_id = (await client.get_entity(base_channel)).id
        
        @client.on(events.Album(chats=channels_to_follow))#, function = produce)
        async def albumHandler(event):
            logger.info(f'album: {event}')
            smsg = [await send_event(msg) for msg in event.messages]
            smsg = parse_telegram_msg(smsg)
            msg_num = cfg.get('msg_num', 1)
            cfg['msg_num'] = (msg_num + 1) % int(os.environ.get('KAFKA_NUM_PARTITIONS', 10))
            logger.info(f'Sending msg {msg_num}')
            producer.send(GATHERING_TOPIC, smsg, key='MESSAGE', partition=msg_num)
            producer.flush()
            raise events.StopPropagation
        
        @client.on(events.NewMessage(incoming=True, chats=channels_to_follow))
        async def handleMsg(event):
            if event.message.grouped_id != None:
                logger.warning(f'********** Found a grouped_id message {event.message} *************8')
                return
            smsg = await send_event(event.message)
            smsg = parse_telegram_msg([smsg])
            msg_num = cfg.get('msg_num', 1)
            cfg['msg_num'] = (msg_num + 1) % int(os.environ.get('KAFKA_NUM_PARTITIONS', 10))
            logger.info(f'Sending msg {msg_num}\n{event.message.to_dict()}')
            producer.send(GATHERING_TOPIC, smsg, key='MESSAGE', partition=msg_num)
            producer.flush()
            raise events.StopPropagation
        
        @client.on(events.NewMessage(blacklist_chats=[base_channel_id, *channels_to_follow]))
        async def simplechat(event):
            logger.debug(f"CHAT: {event.message}")
            
        # @client.on(events.NewMessage(chats=[base_channel_id]))
        # async def simplechat(event):
        #     logger.warning(f"SENT: {event.message}")
            
        await client.run_until_disconnected()

    producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})


## =================================================================
def main(event=None):
    asyncio.run(run())
    if event:
        event.set()



if __name__ == '__main__':
    main()