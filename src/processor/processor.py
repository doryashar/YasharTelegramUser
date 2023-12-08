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
import telethon
# from telethon import TelegramClient, events #, sync
from dotenv import load_dotenv
import os
import random
from datetime import datetime
from .helper_functions import remove_links, remove_ads, remove_duplicates, remove_regexs, remove_signatures
from common_funcs import handle_control_msg
# from ..config import cfg
    
## =================================================================
# Load Configurations:

load_dotenv()
# API_ID  = os.getenv('API_ID', None) 
# API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.
# BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

MYNAME = f'PROCESSOR'#_{random.randint(1,1000)}'
GROUP_ID = os.getenv('GROUP_ID', f'{MYNAME}_TBOT')

#TODO: Fix config module
with open('db/config.json', 'r') as fd:
    cfg = json.load(fd)

## =================================================================

# Load Kafka producer
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, 
                         value_serializer=lambda v: pickle.dumps(v), 
                        #  value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                        #  key_serializer=lambda v: str.encode(v) if v is not None else None
                         )
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()

# Load Kafka Consumer
from kafka import KafkaConsumer
consumer = KafkaConsumer(GATHERING_TOPIC, bootstrap_servers=KAFKA_SERVER,
                         value_deserializer = lambda v: pickle.loads(v),
                        #  value_deserializer = lambda v: json.loads(v.decode('utf-8')),
                        #  auto_offset_reset='earliest', 
                         enable_auto_commit=True,
                         group_id=GROUP_ID,                         
                         )
# consumer.assign([TopicPartition('foobar', 2)]) # Manually assign partition list
consumer.subscribe([CONTROL_TOPIC, GATHERING_TOPIC, PRODUCE_TOPIC])

## =================================================================
def handle_gathering_msg(in_msg):
        out_msg = process(in_msg)
        if out_msg:
            producer.send(PRODUCE_TOPIC, **out_msg)
            producer.flush()
        else:
            logger.info(f'Ignoring {in_msg.value.get("message","No Message")}')
            
def process(msg):
    """ 
    Where the Magic happens
    """

    try:
        msg = msg._asdict() #Convert to class object
        rmsg = msg['value']                
        
        if cfg.get('remove_regexs_from_file', True):
            regexes = None
            if not remove_regexs(rmsg, regexes):
                logger.info(f'Found regex match')
                return False
            
        if cfg.get('remove_ads', True):
            if not remove_ads(rmsg):
                logger.info(f'Found ad')
                return False
            
        if cfg.get('remove_signatures', True):
            if not remove_signatures(rmsg):
                logger.info(f'Found signatures')
                return False
                    
        if cfg.get('remove_links', True):
            rmsg['message'] = remove_links(rmsg['message'])
                
        if cfg.get('remove_duplicates', True):
            if not remove_duplicates(rmsg, latest_messages=latest_messages):
                logger.info(f'Found duplicate')
                return False
            
        if cfg.get('add_channel_alias', True):
            rmsg['message'] = f"{rmsg['from']['chat_title']}:\n{rmsg['message']}"
        
        
        for i in ['topic', 'offset', 'timestamp', 'timestamp_type' ,'checksum', 'serialized_key_size', 'serialized_value_size', 'serialized_header_size']:
            del msg[i]
            
        rmsg['time'] = datetime.now()
        msg['value'] =  rmsg
        msg_id = random.randint(0,999999)
        new_key = f"{msg['key'].decode()}_{msg_id}"
        msg['key'] = new_key.encode()
        
        to_str = {k:v for k,v in rmsg.items() if k != 'files'}
        logger.info(f'Sending msg:\n{to_str}')
        return msg
    
    except Exception as exp:
        logger.error(f'Error retreived in the process func: {exp}', exc_info=True)
        return False

## =================================================================
latest_messages = []
def handle_produce_msg(in_msg): 
    latest_messages.append(in_msg)
    if len(latest_messages) > cfg.get('max_latest_messages', 1000):
        latest_messages.pop(0)
## =================================================================

def main(event=None):
    logger.info("Start listening to MESSAGES")
    num_sent_messages = 0
    num_ignored_messages = 0

    for in_msg in consumer:
        if event and event.is_set():
            break
        
        if in_msg.topic == CONTROL_TOPIC:
            handle_control_msg(in_msg)
        
        elif in_msg.topic == GATHERING_TOPIC:
            handle_gathering_msg(in_msg)
        
        elif in_msg.topic == PRODUCE_TOPIC:
            handle_produce_msg(in_msg)
        
        else:
            logging.error(f'Got unkown msg topic: {in_msg}')
                
    logger.warning('Stopped for some reason')
    producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})

    if event:
        event.set()
        
## =================================================================

if __name__ == '__main__':
    main()
    # metrics = consumer.metrics(), producer.metrics()
    # print(metrics)