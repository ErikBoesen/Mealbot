import os
import requests
import mebots
import random

from flask import Flask, request

app = Flask(__name__)
bot = mebots.Bot('mealbot', os.environ.get('BOT_TOKEN'))

PREFIX = 'mealbot'
GROUP_SIZE = 2

def process(message, instance):
    # Prevent self-reply
    if message['sender_type'] != 'bot':
        if message['text'].lower().startswith(PREFIX):
            group_id = message['group_id']
            bot_id = instance.id
            groupme_token = instance.token
            users = requests.get(f'https://api.groupme.com/v3/groups/{group_id}?token={groupme_token}').json()['response']['members']
            users = [user['name'] for user in users]
            random.shuffle(users)
            pairs = []
            extra = None
            if len(users) % GROUP_SIZE != 0:
                extra = users.pop()
            for i in range(0, len(users), GROUP_SIZE):
                pairs.append(users[i:i + GROUP_SIZE])
            if extra:
                pairs[-1].append(extra)
            return 'Meal pairings:\n--------------\n' + '\n'.join(['- ' + ' & '.join(pair) for pair in pairs])


# Endpoint
@app.route('/', methods=['POST'])
def receive():
    message = request.get_json()
    group_id = message['group_id']
    instance = bot.instance(group_id)
    response = process(message, instance)
    if response:
        send(response, instance.id)

    return 'ok', 200


def send(text, bot_id):
    url  = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)


if __name__ == '__main__':
    while True:
        print(process({'text': input('> '), 'sender_type': 'user', 'group_id': 57639249}))
