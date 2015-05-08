# -*- coding: utf-8 -*-

import datetime
import json
import re
import time
from bitslack import BitSlack, EventHandler

class MessageHandler(EventHandler):
    start_time = None
    def on_event(self, bitslack_obj, event):
        if event['type'] == 'hello':
            bitslack_obj.talk(u'起動しました', '#test')
            self.start_time = time.time()
            return True
        if event['type'] == 'message':
            if float(event['ts']) > self.start_time and \
                '<@USLACKBOT>' in event['text']:
                userid = '<@%s>:' % (event['user'])
                if event['text'] == '<@USLACKBOT>: exit':
                    bitslack_obj.talk(u'終了します', event['channel'])
                    bitslack_obj.end_rtm()
                else:
                    text = re.sub(r'<@USLACKBOT>:?', userid, event['text'])
                    bitslack_obj.talk(text, event['channel'])
            return True
        return False


if __name__ == "__main__":
    import settings
    bslack = BitSlack(settings.SLACK_API_KEY, settings.SLACK_BOT_NAME,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(MessageHandler())
    bslack.start_rtm()
