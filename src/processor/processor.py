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
import telethon
# from telethon import TelegramClient, events #, sync
from dotenv import load_dotenv
import os
import random
    
## =================================================================
# Load Configurations:

load_dotenv()
# API_ID  = os.getenv('API_ID', None) 
# API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.
# BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

KAFKA_SERVER = os.getenv('KAFKA_SERVER',  'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

MYNAME = f'PROCESSOR_{random.randint(1,1000)}'
GROUP_ID = os.getenv('GROUP_ID', f'{MYNAME}_TBOT')
#
#TODO: Add configuration object

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
# consumer.subscribe(['msgpackfoo'])

## =================================================================

def process(msg):
    """ 
    Where the Magic happens
    """
    
    
    #TODO: move to common_funcs
    class tmsg():
        def __init__(self, *args):
            if len(args) == 1: # ConsumerRecord:
                for i, item in enumerate(["topic", "partition", "offset", "timestamp", "timestamp_type", "key", "value", "headers", "checksum", "serialized_key_size", "serialized_value_size", "serialized_header_size"]):
                    setattr(self, item, args[0][i])
            else:
                pass
                #TODO: complete if you want
    
    # Parse the incoming msg
    try:
        msg = tmsg(msg) #Convert to class object
        tbytes = msg.value['tbytes']
        file = msg.value['file']
        # import telethon
        # m = telethon.tl.patched.Message.from_reader(value)
        
        from telethon.extensions import BinaryReader
        smsg = BinaryReader(tbytes).tgread_object()
        logger.info(smsg.to_dict())
        
        msg.value =  smsg, file
        return msg
    
    except Exception as exp:
        logger.error(f'Error retreived in the process func: {exp}', exc_info=True)
        return False

## =================================================================

logger.info("Start listening to MESSAGES")
while True:
    for in_msg in consumer:
        logger.info(in_msg)
        out_msg = process(in_msg)
        if out_msg:
            producer.send(PRODUCE_TOPIC, out_msg.value, key=out_msg.key, headers=out_msg.headers, partition=out_msg.partition)
            producer.flush()
    logger.warning('Stopped for some reason')
    
# metrics = consumer.metrics(), producer.metrics()
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