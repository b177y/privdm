from instagram_private_api import Client, ClientCompatPatch
import json
import time
import datetime
import os
import requests
from cryptography.fernet import Fernet

PATH = os.path.dirname(os.path.abspath(__file__))

def strtime(timenum):
    return datetime.datetime.fromtimestamp((timenum/1000000)).strftime('%Y-%m-%d %H:%M:%S.%f')

def decrypt(data):
    if data == '':
        return data
    try:
        keyfile = open(PATH+'/dmapi.key', 'rb')
        key = keyfile.read()
        keyfile.close()
        f = Fernet(key)
        print("Decrypting password...")
        return f.decrypt(data.encode()).decode()
    except:
        print("Key not found... Password will not be decrypted... Expect incorrect password error")
        return data

def encrypt(data):
    try:
        keyfile = open(PATH+'/dmapi.key', 'rb')
        key = keyfile.read()
        keyfile.close()
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    except FileNotFoundError:
        print("Key not found... Password will not be decrypted... Password will be saved in plaintext")
        return data

