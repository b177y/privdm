from pymongo import MongoClient
import time
from user import user_check
from utils import decrypt
import random
import os

client = MongoClient()
db = client['dmapi']['users']

def random_sleep():
    st = random.randint(20, 28)
    print(f" Waiting {st} seconds", end="")
    for i in range(0, st):
        print(".", end="", flush=True)
        time.sleep(1)
    print("", end="\r")

def return_active_users():
    users = []
    for u in db.find({'active': True}):
        users.append(u)
    return users

def check_all_threads():
    for user in return_active_users():
        print(f"Checking user {user['username']}.                                                                                   ", end="\r")
        updates,updated = user_check(user)
        db.update_one({'_id': user['_id']}, {"$set": updates})
        if updated:
            print(f"\aLatest Sent for {user['username']} at {user['latest_sent']}.", end="", flush=True)
        else:
            print(f"\aNo updates for {user['username']}.", end="", flush=True)

if __name__ == "__main__":
    errors = 0
    print("Starting Server\n")
    while errors < 100:
        try:
            check_all_threads()
            random_sleep()
        except Exception as error:
            print("Error: ", error)
            errors+=1
            print(f"Total errors {errors}\n")
