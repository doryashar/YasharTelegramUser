import re
from .sentense_similarity import text_similarity_check
def remove_links(msg, logger=None):
    # matches = re.findall(r'http\S+', my_string)
    return re.sub('https?://\S+', '', msg)

def set_duplicate(msg, latest_messages): pass #TODO:
def all_images_are_duplicate(msg, latest_messages): pass #TODO

def remove_duplicates(msg, latest_messages=[]):
    if len(msg['message']) > 10 and len([l for l in latest_messages if msg['message'] in l.value['message']]):
        return False
    
    elif set_duplicate(msg, latest_messages):
        return False
    
    elif all_images_are_duplicate(msg, latest_messages):
        return False
    
    elif text_similarity_check(msg, latest_messages):
        return False
    return True

def remove_ads(msg):
    return True

def remove_regexs(msg, rgxes):
    return True