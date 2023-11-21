#unofficial-claude2-api
from claude2_api.client import (
    ClaudeAPIClient,
    SendMessageResponse,
    MessageRateLimitError,
)
from claude2_api.session import SessionData, get_session_data




# Wildcard import will also work the same as above
# from claude2_api import *

# List of attachments filepaths, up to 5, max 20 MB each
FILEPATH_LIST = [
    "test1.txt",
    "test2.txt",
]

# This function will automatically retrieve a SessionData instance using selenium
# Omitting profile argument will use default Firefox profile
data: SessionData = get_session_data()
# or:
# cookie_header_value = "activitySessionId=b10fe9d6-c80b-4fe8-b41b-2065463b08e9; __cf_bm=lrlLnL7suYLx_W3q.3OYkFcEBbOc31RQ_aTlVBVkXs0-1700230456-0-AeIgy9EbwubWZYDjZD4Gqlhsb37yenRYZ17Uqesc9BBu/e98NtPHbU8pOPoHpAMB4hfcBMRwOMCSYPwGjZY4TSc=; cf_clearance=W3oBXivH325VdrEhRg9VBlCY1550NsxO9LhnhHMqiPc-1700230457-0-1-35eab66e.390a8bd6.62ebe98e-0.2.1700230457; __ssid=4deae7097b85a360f43421eadf1fa26; __stripe_mid=bd71050f-1c77-403d-9b2f-e9f4e00a0854f5a092; __stripe_sid=d45d4317-0128-4fbd-a843-dedb7128fd1916b838; sessionKey=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; intercom-session-lupk8zyo=M1pRWVpKUlQrVkJQQkFzeWRxUDhOeUhFRFJXSDF2NE5YWUxQVzNIYld1Z0ViVTJwb1VvckRNZGQ0b1c1UkllZi0tM1R0eXEydFRTVWxqTGgxbkRoTTFSZz09--ac73cfc0fa50f066dc7c796646dcd6b0f14535cb; intercom-device-id-lupk8zyo=3f606b3b-c3a8-47b8-91f0-fb49e30536a6"
# user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
# # cookie_header_value = "The entire Cookie header value string when you visit https://claude.ai/chats"
# # user_agent = "User agent to use, required"
# data = SessionData(cookie_header_value, user_agent)

# Initialize a client instance using a session
client = ClaudeAPIClient(data)

# Create a new chat and cache the chat_id
chat_id = client.create_chat()
if not chat_id:
    # This will not throw MessageRateLimitError
    # But it still means that account has no more messages left.
    print(f"\nMessage limit hit, cannot create chat...")
    quit()

try:
    # Used for sending message with or without attachments
    # Returns a SendMessageResponse instance
    res: SendMessageResponse = client.send_message(
        chat_id, "Hello!", timeout=240 #, attachment_paths=FILEPATH_LIST
    )
    # Inspect answer
    if res.answer:
        print(res.answer)
    else:
        # Inspect response status code and json error
        print(f"\nError code {res.status_code}, response -> {res.error_response}")
except MessageRateLimitError as e:
    # The exception will hold these informations about the rate limit:
    print(f"\nMessage limit hit, resets at {e.resetDate}")
    print(f"\n{e.sleep_sec} seconds left until -> {e.resetTimestamp}")
    quit()
finally:
    # Perform chat deletion for cleanup
    client.delete_chat(chat_id)

# Get a list of all chats ids
all_chat_ids = client.get_all_chat_ids()
# Delete all chats
for chat in all_chat_ids:
    client.delete_chat(chat)

# Or by using a shortcut utility
#
# client.delete_all_chats()