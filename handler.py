import sys
sys.path.insert(0, 'vendor')

import json
import os
import requests
import random

PREFIX = 'mealbot'
GROUP_SIZE = 2


def receive(event, context):
    message = json.loads(event['body'])
    group_id = message['group_id']
    bot_id = message['bot_id']
    token = message['token']
    response = process(message, group_id, token)
    if response:
        send(response, bot_id)

    return {
        'statusCode': 200,
        'body': 'ok',
    }


def process(message, group_id, token):
    # Prevent self-reply
    if message['sender_type'] != 'bot':
        if message['text'].lower().startswith(PREFIX):
            group_id = message['group_id']
            users = requests.get(f'https://api.groupme.com/v3/groups/{group_id}?token={token}').json()['response']['members']
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


def send(text, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)
