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
import json
import telethon
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
from common_funcs import findstem
from src.processor.image_similarity import structural_similarity
import os, re


# class NewsBot:
#     def __init__(self):
#         logging.log('Starting bot')
#         self.cfg = self.get_cfg()
#         self.db  = self.get_db()
#         # self.load_extensions
    
#     def handle_command(self):
#         pass
    
#     def handle_message(self):
#         pass
    
#     def get_cfg(self):
#         return None
    
#     def get_db(self):
#         return None
    
load_dotenv()

# api_hash from https://my.telegram.org, under API Development.
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None) 
client = TelegramClient('Yashar', API_ID, API_KEY)

# Load Configurations:
with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]

















# TODO: this is all should be coming from config or env file
base_channel_name = 'YasharNews'
control_channel_id = 2046544728
duplicate_search_history_length = 500

with open('db/priority-list.txt', 'r') as fd:
    priority_channels = [int(channel.strip()) for channel in fd.readlines()]

chat_signatures = {}
ad_list = []

global removed_messages
with open('db/removed_messages.txt', 'r') as fd:
    removed_messages = [msg[:-2] for msg in fd.readlines()]
    
global ad_regex_items
with open('db/ad_regex_items.txt', 'r') as fd:
    ad_regex_items = [channel[:-2] for channel in fd.readlines()]
    

global latest_photos
latest_photos = []

global remove_to_ignore
remove_to_ignore = 1

global stats
stats = dict()
stats['sent'] = 0
stats['duplicates'] = 0
stats['ads'] = 0

global msg_counter
msg_counter = 0
global sent_messages
sent_messages = []
global latest_messages
latest_messages = []
global group_messages
with open('db/channels_signatures.json', 'r') as openfile: #rb
    group_messages = json.load(openfile)

def rem_channel_to_follow(channel_id):
    channel_id = int(channel_id)
    if channel_id in channels_to_follow:
        channels_to_follow.remove(channel_id)
        with open('db/channel-list.txt', 'w') as fd:
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

async def verify_not_image_or_video_duplicate(message): 
   
    if isinstance(message.media, telethon.tl.types.MessageMediaPhoto):
        # First, we verify different id/checksum
        global latest_photos
        if message.photo.id in [m.id for m in latest_photos] or \
           message.photo.access_hash in [m.access_hash for m in latest_photos]:
            return False
        
        # Then we verify similarity method (1)
        blob = await message.download_media(file=bytes)
        message.photo.blob = blob
        latest_photos = [*latest_photos[:500], message.photo]
        for m in latest_photos:
            if structural_similarity(blob, m.blob) > 0.9:
                logger.info('Found structural similarity')
                return False            
        
        # Then we verify similarity method (2)
        #TODO
        return True
    elif message.media is not None:
        logger.info(f'Found media type: {type(message.media)}')
        # if isinstance(message.media, telethon.tl.types.MessageMediaVideo):
        return True
    
    
    logger.info(message.media) # photo has CONSTRUCTOR_ID, SUBCLASS_OF_ID, dc_id, access_hash, id, file_reference and bytes representation
    
    return True
       
    
    
def verify_not_forwarded_duplicate(message): 
    return True


async def verify_not_duplicate(message):
    global latest_messages
    global stats
    repeated_id_cond = message.id in [m.id for m in latest_messages]
    if repeated_id_cond: 
        stats['duplicates'] += 1
        return False
    
    repeated_fwd_condition = message.fwd_from and (message.fwd_from in [m.fwd_from for m in latest_messages])
    if repeated_fwd_condition:
        stats['duplicates'] += 1
        return False
    
    
    if not await verify_not_image_or_video_duplicate(message):
        stats['duplicates'] += 1
        return False
    
    
    if not verify_not_forwarded_duplicate(message):
        stats['duplicates'] += 1
        return False
    
    if not message.text:
        return True
    
    repeated_text_cond = message.text in [m.text for m in latest_messages]
    if repeated_text_cond:
        stats['duplicates'] += 1
        return False
    
    
    msg_set = set(re.sub('[^A-Za-z0-9 אבגדהוזחטיכלמנסעפצקרךשתןףץם]]+', ' ', message.text).split())
    word_sets = [re.sub('[^A-Za-z0-9 אבגדהוזחטיכלמנסעפצקרךשתןףץם]+', ' ', m.text).split() for m in latest_messages]
    word_sets = [set(m) for m in word_sets]
    
    if len(msg_set) == 0 or len(word_sets) == 0:
        return True
        
    repeated_unique_word_ratio = [len(msg_set.intersection(word))/max([8, min([len(word),len(msg_set)])]) for word in word_sets]
    repeated_unique_word_max_ratio_cond = max(repeated_unique_word_ratio) > 0.7
    repeated_unique_word_cond = any([msg_set == word for word in word_sets])
    
    top_3_msgs = sorted([(msg, repeated_unique_word_ratio[i]) for i, msg in enumerate(latest_messages)], key = lambda x: x[1], reverse=True)[:3]
    repeated_unique_word_ratio_str = '\n'.join([f'{msg.text[:40][::-1]} => {i}' for msg, i in top_3_msgs])
    logger.info(f'for {message.text[:40][::-1]}:\n{repeated_unique_word_ratio_str}\n\n')
    
    if repeated_unique_word_max_ratio_cond or repeated_unique_word_cond:
        stats['duplicates'] += 1
        return False

    return True

    #     logging.info('Found duplicate, ignoring')
    #     return False
    # else:
    #     # latest_messages.pop(0)
    #     # latest_messages.append(message)
    #     latest_messages = [*latest_messages[:999], message]
    #     return True
    
def verify_not_ad(message):
    global removed_messages
    global ad_regex_items
    global stats
    if message.text: 
        for m in removed_messages:
            if message.text.replace('\n',' ') == m:
                stats['ads'] += 1
                return False
    
    for ad_pattern in ad_regex_items:
        if re.match(ad_pattern, message.text):
            stats['ads'] += 1
            return False
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
                with open('db/channel-list.txt', 'a') as fd:
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
                
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)add_regex_item (.*)'))
        async def unfollowchannel(event):
                rgx = event.pattern_match.groups()[0]
                if rgx:
                    global ad_regex_items
                    ad_regex_items.append(rgx)
                    with open('db/ad_regex_items.txt', 'w') as fd:
                        fd.writelines(ad_regex_items)
                    await event.reply(f'OKAY!, added regex match for ads: {rgx}')
                else:
                    await event.reply(f'sorry, could not add regex match for ads: {rgx}')
                    

        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)switch remove_to_ignore(.*)?'))
        async def remove_to_ignore_switch(event):
            #TODO: should be set/switch for general config. if the pattern matches a config then set it
            global remove_to_ignore
            switch = event.pattern_match.groups()[0].lower().strip()
            if switch in ['1', 'on']:
                remove_to_ignore = 1
            elif switch in ['1', 'off']:
                remove_to_ignore = 0
            else:
                remove_to_ignore = not remove_to_ignore   
            await event.reply(f'Remove to ignore is set to {"ON" if remove_to_ignore else "OFF"}')        
                          
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)latest_messages(.*)?'))
        async def unfollowchannel(event):
                count = event.pattern_match.groups()[0] or 0
                latest_messages_ = [m for m in latest_messages if m.text]
                take_msgs = latest_messages_[-int(count):]
                take_msgs = '\n\n'.join([f'{msg.id}) {msg.text}' for msg in take_msgs])
                logging.info(take_msgs)
                await event.reply(f'Latest messages:\n\n{take_msgs}')         
            
        @client.on(events.NewMessage(chats=[2046544728], pattern='(?i)show_stats'))
        async def showstats(event):
            global stats
            stats_str = '\n'.join([f'{key}: {value}' for key, value in stats.items()])
            await event.reply('Stats:\n' + stats_str)
                
        def update_message(message):
            add_title = True #TODO: from config
            if add_title:
                message.text = f'{message.chat.title}:\n{message.text}'
            return message 
        
        def remove_signature(event):
            global group_messages
            global msg_counter
            msg_counter+= 1 % 20
            orig_msg = event.message.text
            if not orig_msg:
                return event.message 
            if not event.chat:
                logger.info(f'event has no chat: {event}')
                return event.message
            
            chat_sig_dict = group_messages.get(event.chat.id, {'latest_messages' : [], 'signatures': []})
            chat_sig_dict['latest_messages'] = [*chat_sig_dict['latest_messages'][-5:], orig_msg]
            to_write = (msg_counter == 0)
            for signature in chat_sig_dict['signatures']:
                event.message.text = event.message.text.replace(signature, '')
            if (len(chat_sig_dict['signatures']) == 0 or orig_msg == event.message.text) and len(chat_sig_dict['latest_messages']) >= 5:
                signature = findstem(chat_sig_dict['latest_messages'])
                if signature:
                    to_write = True
                    logger.info(f'Found new signature {signature}')
                    chat_sig_dict['signatures'].append(signature)
                    event.message.text = event.message.text.replace(signature, '')
            if to_write:
                with open("db/channels_signatures.json", 'w') as f: #wb
                    f.write(json.dumps(group_messages))#, ensure_ascii=False).encode('utf-8'))
            group_messages[event.chat.id] = chat_sig_dict
            return event.message 
        
        @client.on(events.Album(chats=channels_to_follow))
        async def albumHandler(event):
            send_condition = True
            for msg in event.messages:
                send_condition &= await verify_not_duplicate(msg) and verify_not_ad(msg)
            if send_condition or is_priority(event.chat):
                msg = update_message(msg)
                global latest_messages
                latest_messages = [*latest_messages[:duplicate_search_history_length], *[m for m in event.messages if m.text]]
                stats['sent'] += 1
                logger.info(f'Album EVENT: {event}\n')
                await client.send_file(base_channel, event.messages,                                        
                    caption=list(map(lambda a: str(a.message), event.messages)) # message=event.original_update.message.message,  # get the caption message from the album
                )
            
        @client.on(events.NewMessage(incoming=True, chats=channels_to_follow))
        async def handlefollowed(event):
            if event.grouped_id:
                #TODO
                return    # ignore messages that are gallery here
            msg = remove_signature(event)
            msg = copy.copy(event.message)
            send_condition = is_priority(event.chat) or (verify_not_duplicate(msg) and verify_not_ad(msg))
            if send_condition:
                stats['sent'] += 1
                global latest_messages
                latest_messages = [*latest_messages[:duplicate_search_history_length], event.message]
                msg = update_message(msg)
                if msg.forward:
                    logger.info(f'FORWARDED EVENT: {event}\n')
                    p = await event.message.forward_to(base_channel)
                if event.chat.noforwards: #TODO: what about media?
                    logger.info(f'noforwards EVENT: {event}\n')
                    p = await client.send_message(base_channel, msg.text)
                else:
                    logger.info(f'Message EVENT: {event}\n')
                    p = await client.send_message(base_channel, msg)
                event.message.new_id = p.id
            else:
                logging.info(f'Found duplicate, ignoring\n{msg.text}\n')
                # await client.send_read_acknowledge(event.chat, event.message)
            
            
        @client.on(events.MessageDeleted(chats=[base_channel.id]))
        async def handleDelete(event):
            #TODO: what about the media inside?
            global remove_to_ignore
            global removed_messages
            if remove_to_ignore:
                for rm_id in event.deleted_ids:
                    for m in latest_messages[::-1]:
                        if hasattr(m, "new_id") and rm_id  == m.new_id and m.text:
                            removed_messages.append(m.text.replace('\n',' '))
                            with open('db/removed_messages.txt', 'w') as fd:
                                fd.writelines([rm + '\n' for rm in removed_messages])
                            return
                    else:
                        logger.info('Could not find ID to remove')
            
            
        @client.on(events.NewMessage(blacklist_chats=(channels_to_follow + [2046544728, dor.id])))
        async def handleany(event):
            # await event.message.forward_to(dor)
            logging.debug(event)
            
        # @client.on(events.NewMessage(incoming=True, chats=[2046544728]))
        # async def handle_command(event):
        #     logging.info(event)
                
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
    