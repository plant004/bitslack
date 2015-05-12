# -*- coding: utf-8 -*-

import datetime
import json
import re
import thread
import time
from bitslack import BitSlack, EventHandler

class MessageHandler(EventHandler):
    start_time = None
    debug = True

    def on_hello(self, bitslack_obj, event):
        bitslack_obj.talk(u'起動しました', '#test')
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time and \
            '<@USLACKBOT>' in event['text']:
            if self.debug:
                print event['text']
            userid = '<@%s>:' % (event['user'])
            if event['text'] == u'<@USLACKBOT>: exit':
                bitslack_obj.talk(u'終了します', event['channel'])
                bitslack_obj.end_rtm()
            elif u'タイマ' in event['text']:
                sleep_time = self._parse_sleep_time(event['text'])
                timer_text = self._make_timer_text(sleep_time)
                start_time = datetime.datetime.now()
                text = u'%s %s後にタイマを設定しました。(2,3秒の誤差があります。) [%s]' % (userid, timer_text, start_time)
                def run(*args):
                    for i in range(args[0]):
                        time.sleep(1)
                    end_time = datetime.datetime.now()
                    timer_finished = u'%s タイマ設定時刻になりました。 [%s]' % (args[1], end_time)
                    bitslack_obj.talk(timer_finished, event['channel'])
                bitslack_obj.talk(text, event['channel'])
                thread.start_new_thread(run, (sleep_time, userid))

    def _parse_sleep_time(self, text):
        result = 60*3
        text = re.sub(r'<@USLACKBOT>:?', '', text)
        text = re.sub(u'タイマー?[ 　]*', '', text)
        return result

    def _make_timer_text(self, sleep_time):
        result = u'%s秒' % (sleep_time)
        timer_text_list = []
        h, ms = divmod(sleep_time, 3600)
        m, s = divmod(ms, 60)
        if h > 0:
            timer_text_list.append(u'%s時間' % (h))
        if m > 0:
            timer_text_list.append(u'%s分' % (m))
        if s > 0:
            timer_text_list.append(u'%s秒' % (s))
        if len(timer_text_list) > 0:
            result = u'%s' % (u''.join(timer_text_list))
        return result

if __name__ == "__main__":
    import settings
    bslack = BitSlack(settings.SLACK_API_KEY, settings.SLACK_BOT_NAME,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(MessageHandler(settings.SLACK_BOT_NAME))
    bslack.start_rtm()
