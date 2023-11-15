#!/usr/bin/env python

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Main
import copy
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import os, re

base_channel_name = 'YasharNews'
control_channel_id = 2046544728

# api_hash from https://my.telegram.org, under API Development.
load_dotenv()
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None) 
client = TelegramClient('Yashar', API_ID, API_KEY)

with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]

with open('db/priority-list.txt', 'r') as fd:
    priority_channels = [int(channel.strip()) for channel in fd.readlines()]

chat_signatures = {}
ad_list = []
global latest_messages
latest_messages = []
global group_messages
group_messages = dict()


""" 
    Find the stem (longest common substring) from a string array (arr)
    The only modification is that the substring has to be in the edges of the strings and len(substring) > 5
"""
def findstem(arr):
    # Determine size of the array
    n = len(arr)
    # Take first word from array
    # as reference
    s = arr[0]
    l = len(s)
    res = ""
    imax = 0
    for i in range(2):
        for j in range(5, l + 1):
            # generating all possible substrings
            # of our reference string arr[0] i.e s
            stem = s[:j]
            k = 1
            for k in range(1, n):
                # Check if the generated stem is
                # common to all words
                if stem not in arr[k]:
                    break
            # If current substring is present in
            # all strings and its length is greater
            # than current result
            if (k + 1 == n and len(res) < len(stem)):
                res = stem
                imax = i
        s = s[::-1]
    return res[::-1] if imax else res


def rem_channel_to_follow(channel_id):
    channel_id = int(channel_id)
    if channel_id in channels_to_follow:
        channels_to_follow.remove(channel_id)
        with open('channel-list.txt', 'w') as fd:
            fd.writelines([f'{channel}\n' for channel in channels_to_follow])
        
async def join_channel(link_or_name_or_hash, is_hash=False):
    is_url = re.match('https://t.me/(joinchat/)?(.*)',link_or_name_or_hash)
    if is_url:
        is_hash, link_or_name_or_hash = is_url.groups()           
    
    if is_hash:
        from telethon.tl.functions.messages import ImportChatInviteRequest
        updates = await client(ImportChatInviteRequest(link_or_name_or_hash))
    else:
        from telethon.tl.functions.channels import JoinChannelRequest
        updates = await client(JoinChannelRequest(link_or_name_or_hash))
    
    return updates


async def get_channel_list():
        return {dialog.name: dialog.entity async for dialog in client.iter_dialogs() if dialog.is_group or dialog.is_channel}
            
def is_priority(channel):
    return False

def verify_not_duplicate(message):
    global latest_messages
    repeated_id_cond = message.id in [m.id for m in latest_messages]
    msg_set = set(re.sub('[^A-Za-z0-9 אבגדהוזחטיכלמנסעפצקרךשתןףץם]]+', ' ', message.text).split())
    word_sets = [re.sub('[^A-Za-z0-9 אבגדהוזחטיכלמנסעפצקרךשתןףץם]+', ' ', m.text).split() for m in latest_messages]
    word_sets = [set(m) for m in word_sets]
    
    if len(msg_set) == 0 or len(word_sets) == 0:
        latest_messages = [*latest_messages[:999], message]
        return True
    
    repeated_unique_word_ratio = [len(msg_set.intersection(word))/min([len(word),len(msg_set)]) for word in word_sets]
    repeated_unique_word_max_ratio_cond = max(repeated_unique_word_ratio) > 0.7
    
    top_3_msgs = sorted([(msg, repeated_unique_word_ratio[i]) for i, msg in enumerate(latest_messages)], key = lambda x: x[1], reverse=True)[:3]
    repeated_unique_word_ratio_str = '\n'.join([f'{msg.text[:40]} => {i}' for i, msg in top_3_msgs])
    logger.info(f'for {message.text[:40]}:\n{repeated_unique_word_ratio_str}\n\n')
    if ((repeated_id_cond) or (repeated_unique_word_max_ratio_cond)):
        logging.info('Found duplicate, ignoring')
        return False
    else:
        # latest_messages.pop(0)
        # latest_messages.append(message)
        latest_messages = [*latest_messages[:999], message]
        return True
    
def verify_not_ad(message):  
    return True

def main():
    with client:
        dor = client.get_entity('dorito123')
        base_channel = client.get_entity('https://t.me/YasharN3ws')
        control_channel = client.get_entity(control_channel_id)
        client.send_message(control_channel, "Hello, I'm back!")
        logging.info(client.get_me().stringify())
        logging.info(f'following: {channels_to_follow}')
        
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)listchannels'))
        async def list_channels(event):
            channel_list = await get_channel_list()
            channel_list_str = '\n   '.join((channel_list).keys())
            await event.reply(f'Channel list:\n   {channel_list_str}')
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)update'))
        async def list_channels(event):
            client.disconnect()
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)listfollows'))
        async def list_follows(event):
            channel_list = [client.get_entity(channel).name for channel in channels_to_follow]
            channel_list_str = '\n   '.join((channel_list))
            await event.reply(f'Follow list:\n   {channel_list_str}')
                
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)leave (.*)'))
        async def leavechannel(event):
                channel = event.pattern_match.groups()[0]
                # channel_list = await get_channel_list()
                # channel_entity = channel_list.get(channel, None)
                if channel: #channel_entity
                    from telethon.tl.functions.channels import LeaveChannelRequest
                    updates = await client(LeaveChannelRequest(channel))
                    await event.reply(f'OKAY!, left {channel}')
                else:
                    await event.reply(f'ERROR!, cant leave {channel}')
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)join (.*)'))
        async def joinchannel(event):
                channels = event.pattern_match.groups()[0].split()
                for channel in channels:
                    updates = await join_channel(channel)
                    await event.reply(f'OKAY!, joined {channel}')
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)follow (.*)'))
        async def followchannel(event):
                channel = event.pattern_match.groups()[0]
                channel_list = await get_channel_list()
                if channel in channel_list:
                    entityid = channel_list[channel].id
                else:
                    updates = await join_channel(channel)
                    entityid = updates.chats[0].id #await client.get_entity(channel)
                
                channels_to_follow.append(entityid)  
                with open('channel-list.txt', 'a') as fd:
                    fd.write(f'{entityid}\n')
                await event.reply(f'OKAY!, following {channel}({entityid})')
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)unfollow (.*)'))
        async def unfollowchannel(event):
                channel = event.pattern_match.groups()[0]
                # entity = await client.get_entity(channel)
                # entityid = entity.id
                channel_list = await get_channel_list()
                if channel in channel_list:
                    entityid = channel_list[channel].id
                # updates = await leave_channel(channel)
                rem_channel_to_follow(entityid)
                await event.reply(f'OKAY!, unfollowing {channel}')
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)latest_messages(.*)?'))
        async def unfollowchannel(event):
                count = event.pattern_match.groups()[0] or 0
                take_msgs = latest_messages[-int(count):]
                take_msgs = '\n\n'.join([f'{msg.id}) {msg.text}' for msg in take_msgs])
                logging.info(take_msgs)
                await event.reply(f'Latest messages:\n\n{take_msgs}')
                
        
        def update_message(message):
            message.text = f'{message.chat.title}:\n{message.text}'
            return message 
        
        def remove_signature(event):
            global group_messages
            orig_msg = event.message.text
            chat_sig_dict = group_messages.get(event.chat.id, {'latest_messages' : [], 'signatures': []})
            chat_sig_dict['latest_messages'] = [*chat_sig_dict['latest_messages'][-5:], orig_msg]
            for signature in chat_sig_dict['signatures']:
                event.message.text = event.message.text.replace(signature, '')
            if len(chat_sig_dict['signatures']) == 0 or orig_msg == event.message.text:
                signature = findstem(chat_sig_dict['latest_messages'])
                if signature:
                    logger.info(f'Found new signature {signature}')
                    chat_sig_dict['signatures'].append(signature)
                    event.message.text = event.message.text.replace(signature, '')
            group_messages[event.chat.id] = chat_sig_dict
            return event.message 
        
        @client.on(events.NewMessage(chats=channels_to_follow))
        async def handlefollowed(event):
            msg = remove_signature(event)
            msg = copy.copy(event.message)
            if is_priority(event.chat) or (verify_not_duplicate(msg) and verify_not_ad(msg)):
                logging.debug(f'Trying to forward message to {base_channel_name}({base_channel.id})')
                msg = update_message(msg)
                await client.send_message(base_channel, msg)
            else:
                logging.info(f'Found duplicate, ignoring\n{msg.text}')
                # await event.message.forward_to(base_channel)
                # await client.send_read_acknowledge(event.chat, event.message)
            
            
        @client.on(events.NewMessage(blacklist_chats=(channels_to_follow + [2046544728, dor.id])))
        async def handleany(event):
            # await event.message.forward_to(dor)
            logging.debug(event)
                
        client.run_until_disconnected()


# client = TelegramClient('Yashar', API_ID, API_KEY)
# client.start()

# print(client.get_me().stringify())

# client.send_message('dorito123', 'Hello! Talking to you from Telethon')
# # client.send_file('username', '/home/myself/Pictures/holidays.jpg')

# client.download_profile_photo('me')
# messages = client.get_messages('dorito')
# messages[0].download_media()

# @client.on(events.NewMessage(pattern='(?i)hi|hello'))
# async def handler(event):
#     await event.respond('Hey!')

if __name__ == '__main__':
    main()
        


# a = 'עדכון לצפון - רחפן 1 הופל. נוסף התפוצץ. פרטים נוספים בהמשך בהודעת צה"ל'
# b = 'ynet חדשות:\n"עוד נבכה ונתאבל, כרגע צריך לתת שקט לגזרה": הלוחמים שמגינים על גבול הצפון'
# c = 'ביטחון שוטף:\nתקרית חריגה בגדר הגבול בעזה: מחבלים ירו טיל נ״ט לעבר דחפור D-9 של צה״ל שהיה בשטח ישראל, סמוך לגדר באזור כיסופים. שני לוחמי צה״ל נפצעו באורח קשה ובאורח קל. משפחותיהם עודכנו.\nדורון קדוש'
# d = '📌ערוץ החדשות 8200:\nמשרד הבריאות בעזה: "הכוחות נמצאים בקומות התת קרקעיות של בית החולים שיפאא\'"'
# e = 'חדשות ישראל בטלגרם:\n**עדכון לצפון - רחפן 1 הופל. נוסף התפוצץ. פרטים נוספים בהמשך בהודעת צה"ל**'
# f = '"ערוץ הטלגרם חפ"ק מרחב ארצי" 24/7 דיווחים ביטחוניים בזמן אמת:\nטקס סיום קבלת כומתה של בא"ח צנחנים ברצועת עזה . \n\nhttps://t.me/hapaklive'
# g = 'ביטחון שוטף:\nהאם הסעודים מכינים את עצמם על השתלטות על רצועת עזה ביום שאחרי?\n\nמטוס סיוע שביעי המריא מסעודיה למצרים, עמוס בטונות של ציוד הומניטרי'
# h = 'ביטחון שוטף:\n'
# i = 'חדשות בזמן בטלגרם - קבוצת החדשות הגדולה בישראל:\nטיל נ״ט שוגר לעבר כלי הנדסי D-9 באזור כיסופים.\n\nשני לוחמים נפצעו באורח קשה וקל.\nמשפחתם עודכנה.\n\n https://t.me/newss'
# j = 'ביטחון שוטף:\n20 שיגורים נורו לעבר הגליל העליון בדקות האחרונות'

# print([(jellyfish.levenshtein_distance(s, a), jellyfish.jaro_similarity(s, a), jellyfish.damerau_levenshtein_distance(s, a)) for s in [b, c, d, e, f, g, h ,i ,j]])
    