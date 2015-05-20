# -*- coding: utf-8 -*-

import datetime
import json
import re
import time
from bitslack import BitSlack, EventHandler

class HelloHandler(EventHandler):
    start_time = None

    def on_hello(self, bitslack_obj, event):
        bitslack_obj.talk(u'起動しました', '#test', botname=self.name)
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time and \
            u'<@USLACKBOT>' in event['text']:
            userid = '<@%s>:' % (event['user'])
            if event['text'] == u'<@USLACKBOT>: exit':
                bitslack_obj.talk(u'終了します', event['channel'], botname=self.name)
                bitslack_obj.end_rtm()
            else:
                text = re.sub(r'<@USLACKBOT>:?', userid, event['text'])
                bitslack_obj.talk(text, event['channel'], botname=self.name)


if __name__ == "__main__":
    import settings
    botname = u'hello bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(HelloHandler(botname))
    bslack.start_rtm()
