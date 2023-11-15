


# Enable logging
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    filename='run.log'
)
logger = logging.getLogger(__name__)

import importlib
import bot as bot

'''
Done:
+) Git and Dockerize
+) filter similar messages:
    - keep last 1000 messages in array
    - filter out each signature
    - set of unique words
    - Similarity matching - intersection of all the sets in the array divided by length of shortest set > 70%
+) Signature finding mechanism

Tasks:
+) Periodic send message every 5 seconds containing all relevant aggregated messages
+) Prioritize the aggregated messages by chat priority
+) Prioritize the aggregated messages by AI output
+) Add sources and remove middle-man groups (or lower their priority)
+) channel list should have link? user? id? is id the same?
+) counter of interesting channels
+) All channels should be Jsonable Objects (with priority, name, id, link etc) and so does channel-list.txt -> channel_list.json
+) Translate to Hebrew.
+) Semantic similarity
+) Dont forward but send as message, remove signature and add mine.
+) AI if important
+) Remove ads 
    -) admin can add: "add-regex-for-ads"
    -) if admin removes a message, it wont show up again.
+) different channel groups - follow TO channel group.
+) Add logo
+) Multiple bots working together (Bot swarn)
+) If message is too long, split it or summerize it
'''

if __name__ == '__main__':
    while True:
        bot.main()
        logger.info('Reloading bot')
        importlib.reload(bot)