import re
from datetime import datetime
from .sentense_similarity import text_similarity_check
from .image_similarity import structural_similarity

""" 
    Find the stem (longest common substring) from a string array (arr)
"""
def findstem(arr, corners = False, min_len=5):
    # Determine size of the array
    n = len(arr)
    # Take first word from array
    # as reference
    s = arr[0]
    l = len(s)
    res = ""
    imax = 0
    
    def check_stem(s, res=""):
        for j in range(i + min_len, l + 1):
            # generating all possible substrings
            # of our reference string arr[0] i.e s
            stem = s[i:j]
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
        return res
                
    if corners:
        for i in range(l):
            res = check_stem(s, res)
    else:
        i=0
        res1 = check_stem(s)
        res2 = check_stem(s[::-1])[::-1]
        res = res1 if len(res1) > len(res2) else res2
        
    return res

def remove_links(msg, logger=None):
    # matches = re.findall(r'http\S+', my_string)
    return re.sub('https?://\S+', '', msg)

def set_duplicate(msg, latest_messages): pass #TODO:
def any_images_are_duplicate(msg, latest_messages): 
    """
    if a message has an image type file, compare it to latest images
    """
    for file in msg['files']:
        if file['as_image'] == True:
            latest_images = [f['bytes'] for message in latest_messages for f in message.value['files'] if f['as_image'] == True]
            if structural_similarity(file['bytes'], latest_images):
                return True
    return False

def remove_duplicates(msg, latest_messages=[], logger=None):
    # There's a text that was in the latest messages 
    match_similar_cond = lambda texta, text_list, thresh=0.8 : len(findstem([texta, *text_list],corners=False)) > (thresh * len(texta))
    if len(msg['message']) > 10 and match_similar_cond(msg['message'], [l.value['message'] for l in latest_messages if l.value['message']]):
        if logger:
            logger.info(f"Found duplicate message: {msg['message']}\n stem:{findstem([msg['message'], *[l.value['message'] for l in latest_messages if l.value['message']]],corners=False)}\nlatest messages:{[l.value['message'] for l in latest_messages if l.value['message']]}")
        return False
    
    if any_images_are_duplicate(msg, latest_messages):
        if logger:
            logger.info(f"Found duplicate Image")
        return False
    
    # There's no history with messages or current message it too short
    if len(msg['message']) < 10 or len([l for l in latest_messages if l.value['message']]) == 0:
        return True
    
    elif set_duplicate(msg, latest_messages):
        if logger:
            logger.info(f"Found set duplicate")
        return False
    
    elif text_similarity_check(msg['message'], [l.value['message'] for l in latest_messages if l.value['message']]):
        if logger:
            logger.info(f"Found text similarity")
        return False
    return True

import json, os
try:
    with open('db/channels.json', 'r') as f:
        channels = json.load(f)
except:
    channels = dict()
    
def remove_signatures(msg, logger=None):
    if not msg:
       return True
    
    cid = f"{msg['from']['chat_id']}"
    if cid not in channels:
        channels[cid] = {
            'signatures' : [],
            'alias' : msg['from']['chat_title'],
            'admin_username' : None,
            'title' : msg['from']['chat_title'],
            'last_5_msgs' : [msg['message']],
            'last_seen' : f'{datetime.now()}', 
        }
        
    
    channels[cid]['last_5_msgs'].append(msg['message'])
    if len(channels[cid]['last_5_msgs']) > 5:
        channels[cid]['last_5_msgs'].pop(0)
        new_sig = findstem(channels[cid]['last_5_msgs'])
        
        if new_sig:
            #TODO: send it to controller
            if logger:
                logger.info(f"Found a signature for channel [{channels[cid]['alias']}]: {new_sig}")
            channels[cid]['signatures'].append(new_sig)
        
    with open('db/channels.json', 'w') as f:
        json.dump(channels, f)
        
    for signature in channels[cid]['signatures']:
        msg['message'] = msg['message'].replace(signature, '')
        
    return True

def remove_ads(msg):
    return True

def remove_regexs(msg, rgxes):
    return True