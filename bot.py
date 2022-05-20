import json
import random
import re

import emoji
import requests
from autocorrect import Speller
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import config

# account_sid = os.environ['TWILIO_ACCOUNT_SID']
# auth_token = os.environ['TWILIO_AUTH_TOKEN']
# client = Client(account_sid, auth_token)

app = Flask(__name__)


AFFIRM_API = 'https://www.affirmations.dev/'
QUOTE_API = 'https://api.quotable.io/random'


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    reply = process_message(incoming_msg)
    if not reply.responded:
        msg.body(' only know about famous quotes and cats, sorry!')
    else:
        msg.body(reply.text)
        if reply.media:
            msg.media(reply.media)
    return str(resp)


def process_message(incoming_msg):
    # todo account for spelling mistakes
    spell = Speller('en')
    cleaned_msg = spell(incoming_msg.lower())
    bot_response = BotResponse('')
    if re.search('hi|good morning|heya|hello', cleaned_msg):
        bot_response.add_text(emoji.emojize('Hello Bunmi :blush:',language='alias'))

    if 'quote' in cleaned_msg:
        quote = get_quote()
        bot_response.add_text(quote)

    if 'cat' in cleaned_msg:
        bot_response.set_media('https://cataas.com/cat')

    if 'friend' in cleaned_msg:
        bot_response.add_text(random.choice(config.MESSAGE_FROM_FRIENDS))

    if 'feel' in cleaned_msg :
        bot_response.add_text(get_affrimation())
        bot_response.set_media(get_gifh('encourage'))
    return bot_response


class BotResponse:
    def __init__(self, text):
        self.text = text
        self.media = None
        self.responded = False

    def set_media(self, media):
        if not self.responded:
            self.responded = True
        self.media = media

    def add_text(self, text):
        if not self.responded:
            self.responded = True
        if len(self.text) > 0:
            self.text += '\n'
        self.text += text


def get_gifh(search_term):
    lmt = 100
    r = requests.get(
        "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, config.TENOR_API_KEY, lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)
        gif_urls = [gif['media'][0]['mp4']['url'] for gif in top_gifs['results']]
        return random.choice(gif_urls)
    else:
        return None


def get_quote():
    r = requests.get(QUOTE_API)
    if r.status_code == 200:
        data = r.json()
        quote = f'{data["content"]} ({data["author"]})'
    else:
        quote = 'I could not retrieve a quote at this time, sorry.'
    return quote


def get_affrimation():
    r = requests.get(AFFIRM_API)
    if r.status_code == 200:
        data = r.json()
        affirmation = f'{data["affirmation"]})'
    else:
        affirmation = 'I could not retrieve a affirmation at this time, sorry. All I have is YOU GOT THIS!'
    return affirmation


if __name__ == '__main__':
    app.run()
