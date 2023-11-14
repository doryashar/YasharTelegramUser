import importlib
import bot
import logging


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    filename='run.log'
)
logger = logging.getLogger(__name__)


'''
Tasks:
+) Git and Dockerize
+) channel list should have link? user? id? is id the same?
+) filter similar messages:
    - keep last 1000 messages in array
    - filter out each signature
    - find if X in the array. if so don't send it. else add to array
+) counter of interesting channels
+) All channels should be Jsonable Objects (with priority, name, id, link etc) and so does channel-list.txt -> channel_list.json
+) Translate to Hebrew.
+) Dont forward but send as message, remove signature and add mine.
+) AI if important
+) Remove ads
+) follow TO channel group.
+) Add logo
'''

if __name__ == '__main__':
    while True:
        bot.main()
        logging.info('Reloading bot')
        importlib.reload(bot)