


# Enable logging
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    filename='run.log'
)
logger = logging.getLogger(__name__)
logger.info(f'Got logger {__name__}')

import importlib
import threading

from telegram_gatherer import gatherer
from processor import processor
from telegram_broadcaster import broadcaster


'''
Done:
+) Git and Dockerize
+) Dont forward but send as message, remove signature and add mine.
+) filter similar messages:
    - keep last 1000 messages in array
    - filter out each signature
    - set of unique words
    - Similarity matching - intersection of all the sets in the array divided by length of shortest set > 70%
+) Signature finding mechanism
+) Remove ads 
    -) admin can add: "add-regex-for-ads"
    -) if admin removes a message, it wont show up again. activated by switch command, mark by:
            *) message text if there are more than 10 words
            *) images (TBD)

Tasks:
+) Handle images in ads, duplicate messages
+) handle edits
+) Forward/Discard forwarded
+) Each channel should have it's details (username, title, link etc) and add:
    *) a custom alias to show.
    *) Follow to:
    
+) Edits should be propagates
+) Albums should be handled
+) Add configuration
+) Periodic send message every X seconds containing all relevant aggregated messages
+) Prioritize the aggregated messages by chat priority
+) Prioritize the aggregated messages by AI output
+) Add sources and remove middle-man groups (or lower their priority)
+) channel list should have link? user? id? is id the same?
+) counter of interesting channels
+) All channels should be Jsonable Objects (with priority, name, id, link etc) and so does channel-list.txt -> channel_list.json
+) Translate to Hebrew.
+) Semantic similarity
+) AI if important
+) different channel groups - follow TO channel group.
+) Add logo
+) Multiple bots working together (Bot swarn)
+) If message is too long, split it or summerize it
'''

if __name__ == '__main__':
    # while True:
        threading.Thread(target=gatherer.main).start() 
        threading.Thread(target=processor.main).start() 
        threading.Thread(target=broadcaster.main).start() 
        print('Started')
        # logger.info('Reloading bot')
        # importlib.reload(bot)