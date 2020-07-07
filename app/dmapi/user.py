from extendclient import InstaClient
from utils import decrypt, strtime
import json

MEDIATYPES = ["media_share"]

def get_item_params(media_item, recipients):
    i = {}
    f = open("test.json", 'w')
    json.dump(media_item, f)
    f.close()
    if media_item['item_type']=='felix_share':
        print("Felix share")
        i['url'] = media_item['felix_share']['video']['video_versions'][0]['url']
        i['media_type'] = 'video'
    elif media_item['media_share']['media_type'] == 1:
        print("Media type 1")
        i['url'] = media_item['media_share']['image_versions2']['candidates'][0]['url']
        i['media_type'] = 'photo'
    elif media_item['media_share']['media_type'] == 2:
        print("Media type 2")
        i['url'] = media_item['media_share']['video_versions'][0]['url']
        i['media_type'] = 'photo'
    elif media_item['media_share']['media_type'] == 8:
        print("Media type 8")
        i['url'] = media_item['media_share']['carousel_media'][0]['image_versions2']['candidates'][0]['url']
        i['media_type'] = 'photo'
    i['media_id'] = media_item['media_share']['id']
    i['account_pk'] = media_item['media_share']['user']['pk']
    i['account_name'] = media_item['media_share']['user']['username']
    i['private'] = media_item['media_share']['user']['is_private']
    i['timestamp'] = media_item['timestamp']
    i['recipients'] = recipients
    return i

def refine_thread(thread, latest_sent, user_id):
    items = []
    for item in thread['items']:
        if item['timestamp'] <= latest_sent:
            break
        elif str(item['user_id']) == user_id:
            items.append(item)
    items.reverse()
    return items

def parse_items(items):
    items_to_send = []
    for itemindex in range(0, len(items)):
        if items[itemindex]['item_type'] in MEDIATYPES and itemindex != len(items)-1:
            if items[itemindex+1]['item_type'] == "text":
                item = get_item_params(items[itemindex], items[itemindex+1]['text'])
                items_to_send.append(item)
    return items_to_send
    
def user_check(userdata):
    updated = False
    if userdata['settings'] == '':
        api = InstaClient(userdata['username'], decrypt(userdata['password']))
    else:
        api = InstaClient(userdata['username'], "", settings=userdata['settings'])
    updates = {
        'settings' : api.settings
    }
    threadID = api.get_thread_id(userdata['botname'])
    latestthread = api.get_thread_json(threadID)
    items = refine_thread(latestthread, userdata['latest_sent'], userdata['_id'])
    items = parse_items(items)
    for item in items:
        updated = True
        updates['latest_sent'] = item['timestamp']
        recipients = api.get_recipients(item['recipients'], userdata['nicknames'])
        for r in recipients:
            api.send_item(r, item)
    return updates, updated
