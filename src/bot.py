#!/usr/bin/env python

# Main
from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import logging
import os, re

base_channel_name = 'YasharNews'

# api_hash from https://my.telegram.org, under API Development.
load_dotenv()
API_ID  = os.getenv('API_ID', None) 
API_KEY = os.getenv('API_KEY', None) 
client = TelegramClient('Yashar', API_ID, API_KEY)

with open('db/channel-list.txt', 'r') as fd:
    channels_to_follow = [int(channel.strip()) for channel in fd.readlines()]

with open('db/priority-list.txt', 'r') as fd:
    priority_channels = [int(channel.strip()) for channel in fd.readlines()]

latest_messages = []
        

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
    #TODO: list from file
    # if not client:
    #     with open('channel-list.txt', 'r') as fd:
    #         return fd.read()
    # else: 
        return {dialog.name: dialog.entity async for dialog in client.iter_dialogs() if dialog.is_group or dialog.is_channel}
            

def is_priority(channel):
    return False
def verify_not_duplicate(event):
    latest_messages = latest_messages[:999] + event.message
    return True
def verify_not_ad(event):  
    return True

def main():
    with client:
        dor = client.get_entity('dorito123')
        # channel_list = await get_channel_list()
        # base_channel = channel_list[base_channel_name]
        base_channel = client.get_entity('https://t.me/YasharN3ws')
        client.send_message(dor, 'Hello, YASHAR is online!')
        logging.info(client.get_me().stringify())
        #    print(client.download_profile_photo('me'))
            
        
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
                

        @client.on(events.NewMessage(chats=channels_to_follow))
        async def handlefollowed(event):
            channel = 'TODO'
            if not is_priority(channel) and verify_not_duplicate(event) and verify_not_ad(event):
                logging.debug(f'Trying to forward message to {base_channel_name}({base_channel.id})')
                await event.message.forward_to(base_channel)
                # await client.send_read_acknowledge(event.chat, event.message)
            
        @client.on(events.NewMessage(blacklist_chats=(channels_to_follow + [2046544728, dor.id])))
        async def handleany(event):
            # await event.message.forward_to(dor)
            logging.info(event)
                
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