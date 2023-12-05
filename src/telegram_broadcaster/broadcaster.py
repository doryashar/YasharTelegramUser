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
import asyncio
import telethon
from datetime import timedelta
from datetime import datetime as dt
from telethon import TelegramClient, events #, sync
from dotenv import load_dotenv
import os
import random

## =================================================================
# Load Configurations:

load_dotenv()
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None)  # api_hash from https://my.telegram.org, under API Development.
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:29092')
GATHERING_TOPIC = os.getenv('GATHERING_TOPIC', 'gathering')
CONTROL_TOPIC = os.getenv('CONTROL_TOPIC', 'control')
PRODUCE_TOPIC = os.getenv('BROADCAST_TOPIC', 'broadcasting')

MYNAME = f'BROADCASTER'#_{random.randint(1,1000)}'
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
                         key_serializer=lambda v: str.encode(v) if v is not None else None)
producer.send(CONTROL_TOPIC, {MYNAME : 'online!'})
producer.flush()

# Load Kafka Consumer
from kafka import KafkaConsumer
consumer = KafkaConsumer(PRODUCE_TOPIC, bootstrap_servers=KAFKA_SERVER,
                         value_deserializer = lambda v: pickle.loads(v),
                        #  value_deserializer = lambda v: json.loads(v.decode('utf-8')),
                        # auto_offset_reset='earliest', 
                        enable_auto_commit=True,
                        group_id=GROUP_ID)
# consumer.assign([TopicPartition('foobar', 2)]) # Manually assign partition list
# consumer.subscribe(['msgpackfoo'])

## =================================================================
# Get files

async def get_files(smsg):
    smsg['file'] = []
    try:
        for sfile in smsg['files']:
            fd = await bot.upload_file(
                file = sfile.get('bytes'), #_resize_photo_if_needed(file, is_image, width=2560, height=2560, background=(255, 255, 255))
                part_size_kb = sfile.get('part_size_kb', None), #TODO: get from cfg? : float = None,
                file_size = sfile.get('file_size', None), # : int = None,
                file_name = sfile.get('file_name', None) or sfile.get('file_type', None), # : str = None,
                use_cache = sfile.get('use_cache', None), #TODO: get from cfg? # : type = None,
                key = sfile.get('key', None), #TODO: what is this? : bytes = None,
                iv = sfile.get('iv', None), #TODO: what is this? : bytes = None,
                progress_callback = None #TODO: get from cfg?  
            )
            sfile['bytes'] = ''
            # fd.name = sfile.get('file_name', None)
            file_handle, media, image = await bot._file_to_media(
                fd, 
                force_document=sfile.get('force_document', False) ,
                file_size=sfile.get('file_size', None) ,
                progress_callback=None, 
                as_image=sfile.get('as_image', False) ,
                attributes=sfile.get('attributes', None) ,  
                allow_cache=sfile.get('allow_cache', True) , 
                thumb=sfile.get('thumb', None) ,
                voice_note=sfile.get('voice_note', False) , 
                video_note=sfile.get('video_note', False) ,
                supports_streaming=sfile.get('supports_streaming', False) , 
                ttl=sfile.get('ttl', None) ,
                nosound_video=sfile.get('nosound_video', None) , 
                mime_type=sfile.get('mime_type', None) , 
            )
            smsg['file'].append(media)
        if len(smsg['file']) == 1 : smsg['file'] = smsg['file'][0]
        
    except Exception as exp:
        import traceback
        logger.error(f'{smsg} Could not parse smsg\n {traceback.format_exc()}')
        
        
## =================================================================
        
async def run_bot(event=None):    
    global bot
    bot = TelegramClient('bot', API_ID, API_KEY)
    await bot.start(bot_token=BOT_API_TOKEN)

    # dor = bot.get_entity('dorito123')
    base_channel = 'YasharN3WS' #'2092038659' #bot.get_entity('https://t.me/YasharN3ws')

    logger.info("Start listening to MESSAGES")
    for msg in consumer:
            if event and event.is_set():
                break
            
            smsg = msg.value
            # logger.info(f'\nNEW: {smsg}\n')
            # logger.info(f'got message:\n{smsg.__dict__}')
            
            now = dt.now()
            if not isinstance(smsg, dict) or now - smsg.get('time', now + timedelta(hours=2)) > timedelta(hours = 1):
                logger.info(f'Old message was received, ignoring')
                continue 
            elif smsg['message'].startswith('YasharNews:'):
                logger.info(f'YasharNews message was received, ignoring')
                continue 
                
            
            if smsg['files']:
                logger.info('Has file/s. uploading them.')
                await get_files(smsg)
            
            logger.info(f'Sending new message id {msg.key}: \n{smsg}')
            if smsg.get('message',None) == smsg.get('file',None) == None:
                logger.error('ERROR!!')
                continue
            
            try:
                #TODO: send 2 messages if len > 1000
                message = smsg.get('message', '')[:1000] 
                if not message and  isinstance(smsg.get('file', None), list):
                    message = [f['caption'][:1000] for f in smsg['files'] if f['caption']]
                
            except Exception as exp:
                logger.error(f'message error: {exp}\n', exc_info=True)
                continue
                          
            sent_msg = await bot.send_message(
                entity=smsg.get('target_channel', base_channel), #base_channel,
                message=message,
                reply_to=smsg.get('reply_to', None),
                attributes=smsg.get('attributes', None),
                parse_mode=smsg.get('parse_mode', None),
                formatting_entities=smsg.get('formatting_entities', None),
                link_preview=smsg.get('link_preview', None),
                file=smsg.get('file', None),
                thumb=smsg.get('thumb', None),
                force_document=smsg.get('force_document', None),
                clear_draft=smsg.get('clear_draft', None),
                buttons=smsg.get('buttons', None),
                silent=smsg.get('silent', None),
                background=smsg.get('background', None),
                schedule=smsg.get('schedule', None),
                comment_to=smsg.get('comment_to', None),
                #TODO: this can be found In 'file':
                supports_streaming=smsg.get('supports_streaming', None),
                nosound_video=smsg.get('nosound_video', None)
            )
            
            #TODO: update (Broadcast) the sent message id so we can later edit, remove and reply to it
            
            await asyncio.sleep(4)
     
    logger.warning('Stopped for some reason')
    producer.send(CONTROL_TOPIC, {MYNAME : 'going offline'})

## =================================================================

def main(event=None):
    # metrics = consumer.metrics()
    # print(metrics)
    asyncio.run(run_bot(event))
    if event:
        event.set()
if __name__ == '__main__':
    main()