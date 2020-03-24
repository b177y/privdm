try:
    from .utils import encrypt, decrypt
except:
    from utils import encrypt, decrypt
from instagram_private_api import Client, ClientCompatPatch
import os
from cryptography.fernet import Fernet
from pymongo import MongoClient
import time

client = MongoClient()
db = client['dmapi']['users']

def create_user(username, userid, botname="", password="", settings=None, active='False'):
    if password != "":
        password = encrypt(password)
    key = {'_id' : userid}
    newuser = {
        'username' : username,
        'botname' : botname,
        'active' : active
    }
    if settings != None:
        newuser['settings'] = settings
    if db.find(key).count() == 0:
        newuser['nicknames'] = {}
        newuser['latest_sent'] = int(time.time()) * 1000000
        newuser['password'] = password
    db.update(key, {"$set": newuser}, upsert=True)

def update_user(userid, updates):
    try:
        updates = {"$set": updates}
        db.update_one({'_id': userid}, updates)
        return True
    except:
        return False

def set_active(user_id):
    if update_user(user_id, {'active': 'True'}):
        return True
    else:
        return False

def set_inactive(user_id):
    if update_user(user_id, {'active': 'False'}):
        return True
    else:
        return False

def update_latest_sent(user_id, t=int(time.time())):
    update_user(user_id, {'latest_sent': t * 1000000})

def update_nickname(user_id, nickname, username):
    print("Setting nickname {0} to {1} for {2}".format(nickname, username, user_id))
    if ',' in username:
        username = create_gc(username)
    try:
        nn = { "$set" : { "nicknames.{0}".format(nickname) : username } }
        db.update({'_id': user_id}, nn)
    except Exception as error:
        print("Couldn't update usernames: ", error)

def get_userdata(user_id):
    return db.find_one({'_id': user_id})

def delete_nickname(user_id, nickname):
    print("Deleting nickname {0} for {1}".format(nickname, user_id))
    nn = { "$unset" : { "nicknames.{0}".format(nickname) : ""} }
    db.update({'_id': user_id}, nn)

def create_gc(usernames_list):
    usnmList=[]
    for i in usernames_list.split(','):
        i=i.strip()
        usnmList.append(i)
    return usnmList
