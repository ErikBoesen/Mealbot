import os
import requests
import mebots
import random

from flask import Flask, request

app = Flask(__name__)
bot = mebots.Bot('mealbot', os.environ.get('BOT_TOKEN'))

PREFIX = 'mealbot'
GROUPME_ACCESS_TOKEN = os.environ['GROUPME_ACCESS_TOKEN']
GROUP_SIZE = 2

def process(message):
    # Prevent self-reply
    if message['sender_type'] != 'bot':
        if message['text'].lower().startswith(PREFIX):
            #args = message['text'].lstrip(PREFIX).strip().split()
            group_id = message['group_id']
            users = requests.get(f'https://api.groupme.com/v3/groups/{group_id}?token={GROUPME_ACCESS_TOKEN}').json()["response"]["members"]
            users = [user['name'] for user in users]
            random.shuffle(users)
            pairs = []
            if len(users) % GROUP_SIZE != 0:
                extra = users.pop()
            for i in range(0, len(users), GROUP_SIZE):
                pairs.append(users[i:i + GROUP_SIZE])
            pairs[-1].append(extra)
            return '>Meal pairings:\n--------------\n' + '\n'.join(['- ' + ' & '.join(pair) for pair in pairs])


# Endpoint
@app.route('/', methods=['POST'])
def receive():
    message = request.get_json()
    group_id = message['group_id']
    response = process(message)
    if response:
        send(response, group_id)

    return 'ok', 200


def send(text, group_id):
    url  = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot.instance(group_id).id,
        'text': text,
    }
    r = requests.post(url, data=message)


if __name__ == '__main__':
    while True:
        print(process({'text': input('> '), 'sender_type': 'user', 'group_id': 57639249}))
