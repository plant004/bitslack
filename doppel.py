# -*- coding: utf-8 -*-

import datetime
import json
import re
import time
from bitslack import BitSlack, EventHandler

class DoppelHandler(EventHandler):
    start_time = None
    def __init__(self, name, original_name):
        EventHandler.__init__(self, name)
        self.original_name = original_name
        self.original_user = None
        self.original_icon = None
        self.original_mension = None

    def on_hello(self, bitslack_obj, event):
        self.init_original_info(bitslack_obj)
        bitslack_obj.talk(u'起動しました', '#test', botname=self.name)
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time:
            if u'<@USLACKBOT>' in event['text']:
                if event['text'] == u'<@USLACKBOT>: exit':
                    bitslack_obj.talk(u'終了します', event['channel'], botname=self.name)
                    bitslack_obj.end_rtm()
                elif u'doppel' in event['text']:
                    original_name = self._get_username(bitslack_obj, event['text'])
                    self.init_original_info(bitslack_obj, original_name)
                    text = u'%sさんになりすましました。' % (self.original_mension)
                    self.talk_as_original(bitslack_obj, text, event['channel'])
            elif self.original_mension in event['text']:
                userid = '<@%s>:' % (event['user'])
                text = re.sub(r'%s:?' % self.original_mension, userid, event['text'])
                self.talk_as_original(bitslack_obj, text, event['channel'])

    def _get_username(self, bitslack_obj, text):
        result = None
        userid = self._parse_user(text)
        users = bitslack_obj.get_users()
        for username, user in users.items():
            if user['id'] == userid:
                result = username
                break
        return result

    def _parse_user(self, text):
        result = None
        text = re.sub(r'<@USLACKBOT>:?', '', text, count=1)
        match_result = re.search(r'<@(.*?)>', text)
        if match_result is not None:
            result = match_result.group(1)
        return result

    def init_original_info(self, bitslack_obj, original_name=None):
        if original_name is not None:
            self.original_name = original_name
        self.original_user = bitslack_obj.get_user(self.original_name)
        self.original_icon = self._get_icon()
        self.original_mension = u'<@%s>' % (self.original_user['id'])

    def _get_icon(self):
        result = None
        if self.original_user is not None:
            image_key = None
            for k in self.original_user['profile'].keys():
                if 'image_' in k and k != 'image_original':
                    if image_key is None:
                        image_key = k
                    elif int(k[6:]) > int(image_key[6:]):
                        image_key = k
            if image_key is not None:
                result = self.original_user['profile'][image_key]
        return result
   
    def talk_as_original(self, bitslack_obj, texts, channel):
        bitslack_obj.talk(texts, channel, botname=self.original_name, boticon=self.original_icon)
                   
        
if __name__ == "__main__":
    import settings
    botname = u'doppel bot'
    original = '' # target user name
    channel = '#test'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    handler = DoppelHandler(botname, original)
    handler.init_original_info(bslack)
    handler.talk_as_original(bslack, u'hello', channel)
    
    bslack.add_event_handler(handler)
    bslack.start_rtm()
