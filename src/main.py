


# Enable logging
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.info(f'Got logger {__name__}')

import importlib
import threading
import os, sys
import time

'''
+) Signature finding and removing mechanism
+) Each channel should have it's own dict with signature, alias, priority, link, title, type  and where to send

+) filter similar messages:
    - Similarity matching - intersection of all the sets in the array divided by length of shortest set > 70%
+) Remove ads 
    -) admin can add: "add-regex-for-ads"
    -) if admin removes a message, it wont show up again. activated by switch command, mark by:
            *) message text if there are more than 10 words
            *) images (TBD)

+) handle edits/removes/replies and propagate

+) Add controller bot that listen to requests on a channel and spread through control topic:
    -) update
    -) disconnect
    -) configuration update
    -) add/remove channel to follow 
    +) it should verify all are online
    +) whenever exception is raised, it should be written to the channel
    +) Advertise removal confirmation
    
+) Periodic send message every X seconds containing all relevant aggregated messages
+) Prioritize the aggregated messages by chat priority
+) Prioritize the aggregated messages by AI output
+) Add sources and remove middle-man groups (or lower their priority)
+) channel list should have link? user? id? is id the same?
+) counter of interesting channels
+) All channels should be Jsonable Objects (with priority, name, id, link etc) and so does channel-list.txt -> channel_list.json
+) Translate to Hebrew.
+) AI if important
+) different channel groups - follow TO channel group.
+) Add logo
+) Multiple bots working together (Bot swarn)
+) If message is too long, split it or summerize it
'''

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        level=logging.INFO,
        filename='run.log'
    )
    
    logger.info('Now waiting for Kafka to be up and loaded')
    time.sleep(5)
    
    
    from telegram_gatherer import gatherer as telegram_gatherer
    from processor import processor
    from telegram_broadcaster import broadcaster as telegram_broadcaster
    if os.environ['DEBUG_MODE'] == '1':
        sys.argv.extend(['telegram_gatherer', 'processor', 'telegram_broadcaster'])
    
    while True:
        event = threading.Event()
        workers = []
        if 'telegram_gatherer' in sys.argv:
            worker = threading.Thread(target=telegram_gatherer.main, args=(event,))
            worker.start() 
            workers.append(worker)
        if 'processor' in sys.argv:
            worker = threading.Thread(target=processor.main, args=(event,))
            worker.start() 
            workers.append(worker)
        if 'telegram_broadcaster' in sys.argv:
            worker = threading.Thread(target=telegram_broadcaster.main, args=(event,))
            worker.start() 
            workers.append(worker)
        
        print('Started')
        event.wait()
        for worker in workers:
            worker.join()
        importlib.reload(telegram_gatherer)
        importlib.reload(processor)
        importlib.reload(telegram_broadcaster)
        event.clear()
        logger.info('Reloading')