
async def join_channels(client, channels_to_follow):
    joined_channels = await client.get_dialogs()
    joined_channels_ids = [e.id for e in joined_channels]
    for channel in channels_to_follow:
        if channel.id not in joined_channels_ids:
                from telethon.tl.functions.channels import JoinChannelRequest
                client(JoinChannelRequest(channel))
                # from telethon.tl.functions.messages import ImportChatInviteRequest
                # updates = client(ImportChatInviteRequest('AAAAAEHbEkejzxUjAUCfYg'))