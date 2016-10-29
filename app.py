#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import requests

from copy import deepcopy
from flask import Flask, request
from sports import create_session, search_team_name

app = Flask(__name__)

response_template = {
    "message": {
        "recipient": {
            "id": None
        },
        "message": {
            "text": None
        }
    },
    "button": {
        "recipient": {
            "id": None
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': None,
                    'buttons': None
                }
            }
        }
    },
    "action": {
        "recipient": {
            "id": None
        },
        "sender_action": None
    }
}


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


def ask_for_team():
    pass


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
    if '"' in message_text:
        s = create_session('lords')
        team_name = message_text.split('"')[1]
        possible_teams = search_team_name(s, team_name)
        buttons = []
        log(possible_teams)
        for team in possible_teams:  # change this to use generic template \
                    # and element / bubbles
            button = {
                "type": "postback",
                "title": "Team: {}\nDivision: {}\nSession: {}".format(
                    team['name'],
                    team['division'],
                    team['session']
                ),
                "payload": json.dumps({
                    "player_id": sender_id,
                    "team_id": team['id']
                })
            }
            buttons.append(button)
        send_button_message(
            sender_id,
            'Which one is your team?',
            buttons
        )
        # send_text_message(
        #     sender_id, 'Roger-doger, captain.'
        # )
    else:
        send_text_message(
            sender_id, (
                'Sure, whatever. So, what\'s your team name? '
                'Use quotes to indicate the that it\'s the name. '
                'e.g. My team name is "Net-tricks and Skill".'
            )
        )


def postback_router(message):
    sender_id = message["sender"]["id"]
    postback_payload = message["postback"]["payload"]
    if postback_payload:
        send_text_message(sender_id, "posted baaaaaaaack, thanks!")
    # send_postback_message(sender_id)


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
    # [
    #     {
    #         'buttons': [
    #             {
    #                 'type': 'postback',
    #                 'payload': 'DEVELOPER_DEFINED_PAYLOAD',
    #                 'title': 'Bookmark Item'
    #             }
    #         ],
    #         # 'subtitle': 'Soft white cotton t-shirt is back in style',
    #         # 'image_url': \
    #         # 'http://petersapparel.parseapp.com/img/whiteshirt.png',
    #         'title': 'Classic White T-Shirt'
    #     }
    # ]
    log(message)
    post_to_facebook(message)


def post_to_facebook(message):
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
    return r


def log(message):  # simple wrapper for logging to stdout
    print(str(message))
    sys.stdout.flush()
