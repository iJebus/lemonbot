#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import requests

from copy import deepcopy
from flask import Flask, request
from sports import create_session, search_team_name, load_results_page, \
     parse_results_page, next_game

app = Flask(__name__)

response_template = {
    "action": {
        "recipient": {
            "id": None
        },
        "sender_action": None
    },
    "button": {
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': None,
                    'buttons': None
                }
            }
        },
        "recipient": {
            "id": None
        }
    },
    "generic": {
        "message": {
            "attachment": {
                "payload": {
                    "elements": None,
                    "template_type": "generic"
                },
                "type": "template"
            }
        },
        "recipient": {
            "id": None
        }
    },
    "message": {
        "message": {
            "text": None
        },
        "recipient": {
            "id": None
        }
    }
}


@app.route('/', methods=['GET'])
def home():
    return '<h1>Hi :3</h1>'


@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode') == 'subscribe' and \
       request.args.get('hub.verify_token') == os.environ['VERIFY_TOKEN']:
        return request.args.get('hub.challenge')


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                message_event_router(messaging_event)
    return "ok", 200


def message_event_router(messaging_event):
    sender_id = messaging_event["sender"]["id"]
    send_status(sender_id, 'seen')
    send_status(sender_id, 'on')
    if messaging_event.get("message"):
        message_router(messaging_event)
    elif messaging_event.get("postback"):
        postback_router(messaging_event)
    send_status(sender_id, 'off')


def message_router(message):
    sender_id = message["sender"]["id"]
    message_text = message["message"]["text"]
    if 'team:' in message_text.lower():
        s = create_session('lords')
        team_name = message_text.split(':')[1].strip()
        possible_teams = search_team_name(s, team_name)
        if len(possible_teams) > 10:
            send_text_message(
                sender_id, (
                    'Woah, more than ten teams were found. I\'ll show the '
                    'first ten but maybe try again and be more specific.'
                )
            )
        elif not possible_teams:
            send_text_message(
                sender_id, (
                    'No matches :S Case-sensitive at the moment so check that '
                    'and/or your spelling.'
                )
            )
        elements = []
        for team in possible_teams[:10]:
            element = {
                "title": team['name'],
                "subtitle": '{}, {}'.format(team['session'], team['division']),
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Stats",
                        "payload": json.dumps({
                            "player_id": sender_id,
                            "team_id": team['id'],
                            "team_name": team['name'],
                            "action": "stats"
                        })
                    },
                    {
                        "type": "postback",
                        "title": "Next game time",
                        "payload": json.dumps({
                            "player_id": sender_id,
                            "team_id": team['id'],
                            "team_name": team['name'],
                            "action": "next_game"
                        })
                    }
                ]
            }
            elements.append(element)
        send_generic_message(sender_id, elements)
    else:
        send_text_message(
            sender_id, (
                'Sure, whatever. So, what\'s your team name? '
                'I\'m just a dumb robot so say, "Team: Blah" for me to get it.'
            )
        )


def postback_router(message):
    sender_id = message["sender"]["id"]
    postback_payload = message["postback"]["payload"]
    payload = json.loads(postback_payload)
    s = create_session('lords')
    results_page = load_results_page(s, payload['team_id'])
    stats, times = parse_results_page(results_page, payload['team_name'])
    if payload['action'] == 'next_game':
        send_text_message(sender_id, next_game(times))
    elif payload['action'] == 'stats':
        for k, v in stats.iteritems():
            send_text_message(sender_id, k + ': ' + v)


def send_status(recipient_id, status):
    message = deepcopy(response_template['action'])
    message['recipient']['id'] = recipient_id
    if status == 'seen':
        message['sender_action'] = "mark_seen"
    elif status == 'on':
        message['sender_action'] = "typing_on"
    elif status == 'off':
        message['sender_action'] = "typing_off"
    post_to_facebook(message)


def send_text_message(recipient_id, message_text):
    message = deepcopy(response_template['message'])
    message['recipient']['id'] = recipient_id
    message['message']['text'] = message_text
    post_to_facebook(message)


def send_button_message(recipient_id, text, buttons):
    message = deepcopy(response_template['button'])
    message['recipient']['id'] = recipient_id
    message['message']['attachment']['payload']['text'] = text
    message['message']['attachment']['payload']['buttons'] = buttons
    post_to_facebook(message)


def send_generic_message(recipient_id, elements):
    message = deepcopy(response_template['generic'])
    message['recipient']['id'] = recipient_id
    message['message']['attachment']['payload']['elements'] = elements
    post_to_facebook(message)


def post_to_facebook(message):
    log(message)
    data = json.dumps(message)
    r = requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": os.environ['PAGE_ACCESS_TOKEN']},
        headers={"Content-Type": "application/json"},
        data=data
    )
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):
    print(str(message))
    sys.stdout.flush()
