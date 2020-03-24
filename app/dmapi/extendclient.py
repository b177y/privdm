from instagram_private_api import Client, ClientCompatPatch
import json
import urllib.request
from pathlib import Path
DOWNLOAD_LOCATION= str(Path.home()) + "/Downloads"

class InstaClient(Client):
    def findUserID(self, username, nicknames={}):
        username=username.lower()
        if username=="download":
            return 'D'
        if username in nicknames:
            username = nicknames[username]
        if username[0] == '*' and username[-1] == '*':
            thread_id = self.search_for_gc(username[1:-1])[0]
            return 'T' + thread_id
        try:
            userinfo = self._call_api("users/{0}/usernameinfo".format(username))
            return 'U'+str(userinfo['user']['pk'])
        except Exception as error:
            print("Error finding username:", error, username)
            return None
    def get_recipients(self, recipient_list, nicknames={}):
        recipients = []
        for un in recipient_list.split(','):
            un = un.strip()
            recipients.append(self.findUserID(un, nicknames))
        return recipients
    def direct_message(self, recipient, message, thread_id=0):
        endpoint = 'direct_v2/threads/broadcast/text/'
        params = {
            'text' : message,
        }
        if recipient != "":
            params['recipient_users'] = '[["{}"]]'.format(recipient),
        if thread_id != 0:
            params['thread_ids'] = '["{}"]'.format(thread_id)
        self._call_api(endpoint, params, unsigned=True)
    def direct_link(self, recipient, link, thread_id=0):
        endpoint = 'direct_v2/threads/broadcast/link/'
        params = {
            'link_text' : "Post shared from Billy's Meme 🅱️ot ting: 🔗 {0}  ( ℹ️ @privdm_api )".format(link),
            'link_urls' : json.dumps([link])
        }
        if recipient != "":
            params['recipient_users'] = '[["{}"]]'.format(recipient),
        if thread_id != 0:
            params['thread_ids'] = '["{}"]'.format(thread_id)
        self._call_api(endpoint, params, unsigned=True)
    def direct_share(self, recipient, media_id, mtype, thread_id=0):
        endpoint = 'direct_v2/threads/broadcast/media_share/?media_type={0}'.format(mtype)
        params = {
            'media_id' : media_id
        }
        if recipient != "":
            params['recipient_users'] = '[["{}"]]'.format(recipient),
        if thread_id != 0:
            params['thread_ids'] = '["{}"]'.format(thread_id)
        self._call_api(endpoint, params, unsigned=True)
    def download_item(self, item):
        url = item['url']
        ext = "jpg" if item['media_type'] == 'photo' else "mp4"
        fn = f"{DOWNLOAD_LOCATION}/{item['timestamp']}.{ext}"
        print(f"Downloading to {fn}")
        urllib.request.urlretrieve(url, fn)
    def check_following(self, recipient, account_name):
        print("Checking if {0} is following {1}...".format(recipient, account_name), end="")
        query = self.user_following(recipient, self.generate_uuid(), query=account_name)
        for q in query['users']:
            if q['username'] == account_name:
                print("Yeep")
                return True
        print("Noop")
        return False
    def check_all_following(self, account_name, rec, thread_id):
        if rec != "":
            return self.check_following(rec, account_name)
        elif thread_id != 0:
            users = self.get_thread_json(thread_id)['users']
            for u in users:
                if not self.check_following(u['pk'], account_name):
                    return False
            return True
        return False
    def search_for_gc(self, name):
        threads = self.direct_v2_inbox()
        possibilities = ['0']
        for t in threads['inbox']['threads']:
            if t['thread_title'] == name:
                return [t['thread_id']]
            elif name.lower() in t['thread_title'].lower():
                possibilities.prepend(t['thread_id'])
        return possibilities
    def get_thread_id(self, botname):
        threads = self.direct_v2_inbox()
        for t in threads['inbox']['threads']:
            if len(t['users']) == 1 and t['users'][0]['username'] == botname:
                return t['thread_id']
        return None
    def get_thread_json(self, threadID):
        custom_req = "direct_v2/threads/{0}".format(threadID)
        return self._call_api(custom_req)['thread']
    def send_item(self, recipient, item):
        print(f"Sending {item['media_type']} to {recipient}")
        if recipient == None:
            return
        rec = ""
        thread_id = 0
        if recipient[0] == 'T':
            thread_id = recipient[1:]
        elif recipient[0] == 'U':
            rec = recipient[1:]
        if recipient == 'D':
            self.download_item(item)
        elif item['private'] == False:
            self.direct_share(rec, item['media_id'], item['media_type'], thread_id=thread_id)
        elif self.check_all_following(item['account_name'], rec, thread_id):
            self.direct_share(rec, item['media_id'], item['media_type'], thread_id=thread_id)
        else:
            self.direct_link(rec, item['url'], thread_id=thread_id)
