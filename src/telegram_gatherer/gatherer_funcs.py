from telethon.extensions import BinaryReader
import copy
import json
import telethon
import logging
async def join_channels(client, channels_to_follow):
    joined_channels = await client.get_dialogs()
    joined_channels_ids = [e.entity.id for e in joined_channels if e.is_channel or e.is_group]
    logging.info(f'joined_channels_ids={joined_channels_ids} channels={channels_to_follow}')
    for channel in channels_to_follow:
        if channel not in joined_channels_ids:
                logging.info(f'joining {channel}')
                from telethon.tl.functions.channels import JoinChannelRequest
                await client(JoinChannelRequest(channel))
                # from telethon.tl.functions.messages import ImportChatInviteRequest
                # updates = client(ImportChatInviteRequest('AAAAAEHbEkejzxUjAUCfYg'))
                


#TODO: broadcast should be something like this, need to parse:
def parse_telegram_msg(msgs, logger=logging):
    if not isinstance(msgs, list):
        msgs = [msgs]
        
    send_message_dict = dict()
    
    try:
        for i, msg in enumerate(msgs): 
            smsg, rmedia = msg['msg'], msg['media']
            
            if isinstance(smsg, bytes):
                smsg = BinaryReader(smsg).tgread_object()
            
            """
            {'out': False, 'mentioned': False, 'media_unread': False, 'silent': False, 'post': True, 'from_scheduled': False, 'legacy': False, 'edit_hide': False, 'id': 36984, 'from_id': None, 'peer_id': <telethon.tl.types.PeerChannel object at 0x7f688f224fa0>, 'fwd_from': None, 'via_bot_id': None, 'reply_to': None, 'date': datetime.datetime(2023, 11, 26, 15, 55, 21, tzinfo=datetime.timezone.utc), 'message': 'ברשימת המשוחררים והמשוחררות שהועברו לצלב האדום - 9 ילדים | השמות והסיפורים', 'media': <telethon.tl.types.MessageMediaPhoto object at 0x7f688f2250f0>, 'reply_markup': None, 'entities': [<telethon.tl.types.MessageEntityTextUrl object at 0x7f688f2254b0>], 'views': 1, 'forwards': 0, 'replies': None, 'edit_date': None, 'pinned': False, 'noforwards': False, 'invert_media': False, 'post_author': None, 'grouped_id': None, 'reactions': None, 'restriction_reason': None, 'ttl_period': None, 'action': None, '_client': None, '_text': None, '_file': <telethon.tl.custom.file.File object at 0x7f688f2253f0>, '_reply_message': None, '_buttons': None, '_buttons_flat': None, '_buttons_count': 0, '_via_bot': None, '_via_input_bot': None, '_action_entities': None, '_linked_chat': None, '_chat_peer': <telethon.tl.types.PeerChannel object at 0x7f688f224fa0>, '_input_chat': <telethon.tl.types.InputPeerChannel object at 0x7f688f225510>, '_chat': <telethon.tl.types.Channel object at 0x7f688f2255a0>, '_broadcast': True, '_sender_id': -1001397114707, '_sender': <telethon.tl.types.Channel object at 0x7f688f2255a0>, '_input_sender': <telethon.tl.types.InputPeerChannel object at 0x7f688f2256f0>, '_forward': None}
            Media: {'spoiler': False, 'photo': <telethon.tl.types.Photo object at 0x7f688f224e50>, 'ttl_seconds': None}
            Media.photo:  {'id': 5990034272204996845, 'access_hash': -6337763010793853029, 'file_reference': b"\x02SFGS\x00\x00\x90xecji\xa9\xdaG\xfb'\xbb\x8d\xf1N\x16\x9f\x99\x82\xafa\xba", 'date': datetime.datetime(2023, 11, 26, 15, 23, 8, tzinfo=datetime.timezone.utc), 'sizes': [<telethon.tl.types.PhotoStrippedSize object at 0x7f688f2252a0>, <telethon.tl.types.PhotoSize object at 0x7f688f225360>, <telethon.tl.types.PhotoSize object at 0x7f688f225330>, <telethon.tl.types.PhotoSizeProgressive object at 0x7f688f225390>], 'dc_id': 4, 'has_stickers': False, 'video_sizes': None} <- Add more
            Entities:{'offset': 58, 'length': 16, 'url': 'https://bit.ly/3uy6Tk3'} <- ADD more
            Peer_ID: {'channel_id': 1397114707}
            _file, _chat_peer, _input_chat, _chat, _sender, _input_sender <- TBD
            
            
            {'_': 'Message', 'id': 57341, 'peer_id': {'_': 'PeerChannel', 'channel_id': 1462917933}, 'date': datetime.datetime(2023, 11, 26, 14, 46, 13, tzinfo=datetime.timezone.utc), 'message': '', 'out': False, 'mentioned': False, 'media_unread': False, 'silent': False, 'post': True, 'from_scheduled': False, 'legacy': False, 'edit_hide': True, 'pinned': False, 'noforwards': False, 'invert_media': False, 'from_id': None, 'fwd_from': None, 'via_bot_id': None, 'reply_to': None, 'media': {'_': 'MessageMediaDocument', 'nopremium': False, 'spoiler': False, 'document': {'_': 'Document', 'id': 5987664467708613112, 'access_hash': -716869027500490831, 'file_reference': b'\x02W2[-\x00\x00\xdf\xfdecZD~\xcd\x11\xf3\x96W\x13s\xd12\xdd\xb7\x94\nl\xed', 'date': datetime.datetime(2023, 11, 26, 14, 46, 13, tzinfo=datetime.timezone.utc), 'mime_type': 'video/mp4', 'size': 262728, 'dc_id': 4, 'attributes': [
            {'_': 'DocumentAttributeVideo', 'duration': 3.5, 'w': 352, 'h': 640, 'round_message': False, 'supports_streaming': True, 'nosound': False, 'preload_prefix_size': None}, {'_': 'DocumentAttributeFilename', 'file_name': 'IMG_9086.MP4'}], 'thumbs': [{'_': 'PhotoStrippedSize', 'type': 'i', 'bytes': b'\x01(\x16\xb0\x84\x93\x8cqRb\x9a\xac\x00\xea(f\x07\xb8\xfc\xea\xaeM\x87b\x8ag^\xa7\x02\x8a9\x82\xc5t/\x90s\xd0t\xa92MD\x0f\x14\xb9\x1d\xe9Xw$\xc9\xf6\xa2\xa2\xcd\x14X.WIY\x87jr\x9erh\xa2\x98\x87\xee\xcfz(\xa2\x80?'}, {'_': 'PhotoSize', 'type': 'm', 'w': 176, 'h': 320, 'size': 6078}], 'video_thumbs': []}, 'alt_document': None, 'ttl_seconds': None}, 'reply_markup': None, 'entities': [], 'views': 1, 'forwards': 0, 'replies': None, 'edit_date': datetime.datetime(2023, 11, 26, 14, 46, 16, tzinfo=datetime.timezone.utc), 'post_author': 'משה', 'grouped_id': 13608079788316596, 'reactions': None, 'restriction_reason': [], 'ttl_period': None}

            """
            if (i == 0):
                send_message_dict.update({
                            # 'target_channel': TODO: base_channel, #'hints.EntityLike',                            
                            'message': smsg.message, #'hints.MessageLike' = '',
                            'reply_to': None, #TODO: get error smsg.reply_to TypeError: Invalid message type: <class 'telethon.tl.types.MessageReplyHeader'> , #'typing.Union[int, types.Message]' = None,
                            'attributes': None, #TODO: what is that? in every msg? #'typing.Sequence[types.TypeDocumentAttribute]' = None,
                            'parse_mode': (), #typing.Optional[str] = (),
                            'formatting_entities': None, #TODO: what is that? can be found under smsg.photo/smsg.video #typing.Optional[typing.List[types.TypeMessageEntity]] = None,
                            'link_preview': True, #TODO: where do i get it from? #bool = True,
                            'thumb': None, #TODO: take from media #'hints.FileLike' = None,
                            'force_document': False, #TODO: Where from? bool = False,
                            'clear_draft': False, #What is that? #bool = False,
                            'silent': smsg.silent, #bool = None,
                            'background': None, #TODO: where from ?#bool = None,
                            'schedule': None, #'hints.DateLike' = None,
                            'comment_to': None, #TODO: where from? #'typing.Union[int, types.Message]' = None,
                            'buttons': smsg.buttons, #typing.Optional['hints.MarkupLike'] = None,                
                            
                            ## Extra info
                            'files': [], #TODO: what about stickers? #'typing.Union[hints.FileLike, typing.Sequence[hints.FileLike]]' = None,                        
                            'from' : { 
                                'chat_id' : smsg.chat.id,
                                'chat_title' : smsg.chat.title,
                                'from_user' : None,
                                'via_input_bot' : smsg.via_input_bot, 
                                'via_bot' : smsg.via_bot, 
                                'via_bot_id' : smsg.via_bot_id,
                                'fwd_from' : smsg.fwd_from,  
                                'forward' : smsg.forward, 
                                #TODO: continue
                            },
                            
                            'forwards' : smsg.forwards,
                            'web_preview' : smsg.web_preview,
                            'venue' :  smsg.venue,    
                            'views' :  smsg.views,   
                            'pinned' :  smsg.pinned,   
                            'poll' :  smsg.poll,   
                            'post' :  smsg.post,   
                            'post_author' :  smsg.post_author,  
                            'mentioned' :  smsg.mentioned,   
                            'is_group' :  smsg.is_group,   
                            'is_channel' :  smsg.is_channel,   
                            'is_private' :  smsg.is_private,   
                            'is_reply' :  smsg.is_reply,   
                            'chat_id' : smsg.chat_id,
                            'id' : smsg.id,
                            #replies
                            #reply_markup
                            #reactions
                            #sender
                            #entities
                })
                send_message_dict.update({
                    j: getattr(smsg,j) for j in ['game', 'geo', 'gif', 'forwards', 'legacy', 'media_unread', 'noforwards', 'reply_to_msg_id', 'restriction_reason', 'dice', 'edit_date', 'edit_hide', 'button_count', 'action']
                }) #'action_entites', 'forward',
            
            if rmedia: #isinstance(smsg.media, telethon.tl.types.MessageMediaPhoto):
                file_dict = {
                    'bytes' : rmedia,
                    'file_name' : smsg.file.name, # or 'rand' + smsg.file.ext, #I have Added
                    'file_size': smsg.file.size, # TODO int = None,
                    # 'nosound_video': False, #TODO: where from? #bool = None,
                    'caption': smsg.file.title, #typing.Union[str, typing.Sequence[str]] = None,
                    'mime_type' : smsg.file.mime_type,
                    # 'supports_streaming': False, #TODO: where from? #bool = False,
                    # 'progress_callback': None, #'hints.ProgressCallback' = None,
                    # 'allow_cache': True, #bool = True,
                    
                    'voice_note': None, # TODO: not there: smsg.voice_note, #bool = False,
                    'video_note': None, #TODO: not there? smsg.video_note, #bool = False,
                    'as_image': smsg.photo is not None, #bool = False,
                    # 'ttl': None, #int = None,
                    
                    ## Extra info:
                    'file_type' : smsg.file.ext, #I have Added
                    'sticker_set' : smsg.file.sticker_set,
                    'emoji' : smsg.file.emoji,
                    'duration' : smsg.file.duration,
                    'height' : smsg.file.height,
                    'width' : smsg.file.width,
                    'performer' : smsg.file.performer, 
                }
                if isinstance(smsg.file.media, telethon.tl.types.Photo):
                    file_dict.update({
                        # media 
                        'media_date' : smsg.file.media.date,
                        'media_sizes' : smsg.file.media.sizes,
                        'media_video_sizes' : smsg.file.media.video_sizes,
                        'has_stickers' : smsg.file.media.has_stickers,
                    })
                elif isinstance(smsg.file.media, telethon.tl.types.Document):
                    file_dict.update({                        
                        'thumbs' : smsg.file.media.thumbs,
                        'video_thumbs': smsg.file.media.video_thumbs,
                        # 'no_premium': smsg.file.media.no_premium,
                        # 'spoiler': smsg.file.media.spoiler,
                    })
                else:
                    logger.error(f'Unknown type: {type(smsg.file.media)}')
                    
                send_message_dict['files'].append(file_dict)
                
        pretty_dict = lambda d : json.dumps(d, sort_keys=True, indent=4, default=str)
        send_message_dict_cp = copy.deepcopy(send_message_dict)
        for i in range(len(send_message_dict_cp['files'])):
            send_message_dict_cp['files'][i]['bytes'] = None
            
        logger.debug(f'\nParsed from (asdict):\n{pretty_dict(smsg.to_dict())}\nTo:\n{pretty_dict(send_message_dict_cp)}') 
        
    
    except Exception as exp:
        logger.error(exp)
    
    return send_message_dict
    
## =================================================================                