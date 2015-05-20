# -*- coding: utf-8 -*-

import datetime
import json
import re
import thread
import time
from bitslack import BitSlack, EventHandler

class TimerHandler(EventHandler):
    start_time = None
    debug = True

    def on_hello(self, bitslack_obj, event):
        bitslack_obj.talk(u'起動しました', '#test', botname=self.name)
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time and \
            u'<@USLACKBOT>' in event['text']:
            if self.debug:
                print event['text']
            userid = '<@%s>:' % (event['user'])
            if event['text'] == u'<@USLACKBOT>: exit':
                bitslack_obj.talk(u'終了します', event['channel'], botname=self.name)
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
                    bitslack_obj.talk(timer_finished, event['channel'], botname=self.name)
                bitslack_obj.talk(text, event['channel'], botname=self.name)
                thread.start_new_thread(run, (sleep_time, userid))

    def _parse_sleep_time(self, text):
        result = 60*3
        text = re.sub(r'<@USLACKBOT>:?', '', text)
        text = re.sub(u'タイマー?[ 　]*', '', text)
        
        hhmm_patterns = [
            r'(\d{1,2}):(\d{1,2})',
            u'(\d{1,2})時(\d{1,2})分',
        ]
        for hhmm_pattern in hhmm_patterns:
            
            match_result = re.search(hhmm_pattern, text)
            if match_result is not None:
                h = int(match_result.group(1))
                m = int(match_result.group(2))
                now_datetime = datetime.datetime.now()
                timer_datetime = datetime.datetime(now_datetime.year, now_datetime.month, now_datetime.day, h, m)
                if timer_datetime < now_datetime:
                    timer_datetime = timer_datetime + datetime.timedelta(days=1)
                delta = timer_datetime - now_datetime
                result = delta.days * 86400 + delta.seconds
                break
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
    botname = 'timer bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(TimerHandler(botname))
    bslack.start_rtm()
