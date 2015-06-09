# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import datetime
import json
import re
import thread
import time
from bitslack import BitSlack, EventHandler

class TimerHandler(EventHandler):
    start_time = None
    debug = False
    TIMER_PATTERNS = [
        u'タイマ',
        u'set_timer',
    ]
    PATTERN_TYPE_HH = 1
    PATTERN_TYPE_MM = 2
    PATTERN_TYPE_AFTER = 4
    PATTERN_TYPE_HHMM = PATTERN_TYPE_HH|PATTERN_TYPE_MM
    PATTERN_TYPE_HH_AFTER = PATTERN_TYPE_HH|PATTERN_TYPE_AFTER
    PATTERN_TYPE_MM_AFTER = PATTERN_TYPE_MM|PATTERN_TYPE_AFTER
    PATTERN_TYPE_HHMM_AFTER = PATTERN_TYPE_HHMM|PATTERN_TYPE_AFTER
    interactive_status_map = {}

    def __init__(self, name=None):
        EventHandler.__init__(self, name)
        description = u'タイマーを設定します。'.encode('utf-8')
        self.parser = ArgumentParser(description=description, prog=u'@slackbot タイマ|set_timer'.encode('utf-8'), add_help=False)

        self.parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))
        self.parser.add_argument('-m', '--message', dest='message', default='', help=u'タイマー設定時刻になった場合に表示するメッセージを指定します。'.encode('utf-8'))

        self.parser.add_argument('time', help=u'タイマー設定時刻(HH:mm, HH時mm分、HH時間後,mm分後など)'.encode('utf-8'))
    def on_hello(self, bitslack_obj, event):
        bitslack_obj.talk(u'起動しました', '#test', botname=self.name)
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time and \
            u'<@USLACKBOT>' in event['text']:
            if self.debug:
                print event['text']
            if event['text'] == u'<@USLACKBOT>: exit':
                bitslack_obj.talk(u'終了します', event['channel'], botname=self.name)
                bitslack_obj.end_rtm()
            else:
                self._handle(bitslack_obj, event)

    def _handle(self, bitslack_obj, event):
        userid = '<@%s>:' % (event['user'])
        if self._is_timer_command(event):
                text_list = event['text'].split()
                args, unknown_args = self.parser.parse_known_args(text_list)
                if args.usage:
                    usage = self.parser.format_help()
                    bitslack_obj.talk(usage.decode('utf-8'), event['channel'], botname=self.name)
                    return
                sleep_time, timer_text = self._parse_sleep_time(event['text'])
                start_time = datetime.datetime.now()
                text = u'%s %sにタイマを設定しました。' % (userid, timer_text)
                def run(*args):
                    time.sleep(args[0])
                    end_time = datetime.datetime.now()
                    #timer_finished = u'%s タイマ設定時刻になりました。' % (args[1], end_time)
                    timer_finished = u'%s タイマ設定時刻になりました。%s' % (args[1], args[2])
                    bitslack_obj.talk(timer_finished, event['channel'], botname=self.name)
                bitslack_obj.talk(text, event['channel'], botname=self.name)
                thread.start_new_thread(run, (sleep_time, userid, args.message))

    def _is_timer_command(self, event):
        result = False
        for pattern in TimerHandler.TIMER_PATTERNS:
            if pattern in event['text']:
                result = True
                break
        return result

    def _parse_sleep_time(self, text):
        result = None
        text = re.sub(r'<@USLACKBOT>:?', '', text)
        text = re.sub(u'タイマー?[ 　]*', '', text)

        hhmm_after_patterns = [
            u'(\d{1,2})時間(\d{1,2})分後',
        ]

        hhmm_patterns = [
            u'(\d{1,2}):(\d{1,2})',
            u'(\d{1,2})時(\d{1,2})分',
        ]

        hh_after_patterns = [
            u'(\d{1,2})時間後',
        ]

        hh_patterns = [
            u'(\d{1,2})時',
        ]

        mm_after_patterns = [
            u'(\d{1,2})分後',
        ]

        mm_patterns = [
            u'(\d{1,2})分',
        ]

        match = self._match_time_patterns(text, hhmm_after_patterns, TimerHandler.PATTERN_TYPE_HHMM_AFTER)
        if match is None:
            match = self._match_time_patterns(text, hhmm_patterns, TimerHandler.PATTERN_TYPE_HHMM)
        if match is None:
            match = self._match_time_patterns(text, hh_after_patterns, TimerHandler.PATTERN_TYPE_HH_AFTER)
        if match is None:
            match = self._match_time_patterns(text, hh_patterns, TimerHandler.PATTERN_TYPE_HH)
        if match is None:
            match = self._match_time_patterns(text, mm_after_patterns, TimerHandler.PATTERN_TYPE_MM_AFTER)
        if match is None:
            match = self._match_time_patterns(text, mm_patterns, TimerHandler.PATTERN_TYPE_MM)

        if match is not None:
            match_text = match[0]
            h = int(match[1])
            m = int(match[2])
            after_flg = match[3]
            now_datetime = datetime.datetime.now()
            s = 0
            days_delta = 0
            if after_flg:
                s = now_datetime.second
                if m < 0:
                    m = now_datetime.minute
                else:
                    m = now_datetime.minute + m
                if h < 0:
                    h = now_datetime.hour
                else:
                    h = now_datetime.hour + h
            else:
                if m < 0:
                    m = 0
                if h < 0:
                    h = now_datetime.hour
            if 59 < m:
                h_delta, new_m = divmod(m, 60)
                h = h + h_delta
                m = new_m
            if 23 < h:
                d_delta, new_h = divmod(h, 24)
                days_delta = d_delta
                h = new_h
            #print '%s:%s' % (h, m)
            timer_datetime = datetime.datetime(now_datetime.year, now_datetime.month, now_datetime.day, h, m, s)
            timer_datetime = timer_datetime + datetime.timedelta(days=days_delta)
            if timer_datetime < now_datetime:
                timer_datetime = timer_datetime + datetime.timedelta(days=1)
            delta = timer_datetime - now_datetime
            sleep_time = delta.days * 86400 + delta.seconds
            match_text = self._make_timer_text(sleep_time+1, after_flg)
            result = [sleep_time, match_text]
        return result

    def _match_time_patterns(self, text, patterns, pattern_types):
        result = None
        match_text = None
        h = -1
        m = -1
        after_flg = False
        for pattern in patterns:
            match = re.search(pattern, text)
            if match is not None:
                match_text = match.group(0)
                if TimerHandler.PATTERN_TYPE_HH & pattern_types:
                    h = match.group(1)
                    if TimerHandler.PATTERN_TYPE_MM & pattern_types:
                        m = match.group(2)
                    
                elif TimerHandler.PATTERN_TYPE_MM & pattern_types:
                    m = match.group(1)
                if TimerHandler.PATTERN_TYPE_AFTER & pattern_types:
                    after_flg = True
                result = (match_text, h, m, after_flg)
                break
        return result

    def _make_timer_text(self, sleep_time, after_flg):
        result = u'%s秒' % (sleep_time)
        timer_text_list = []
        h, ms = divmod(sleep_time, 3600)
        m, s = divmod(ms, 60)
        if after_flg:
            if h > 0:
                timer_text_list.append(u'%s時間' % (h))
            if m > 0:
                timer_text_list.append(u'%s分' % (m))
            if s > 0:
                timer_text_list.append(u'%s秒' % (s))
            if len(timer_text_list) > 0:
                result = u'%s後' % (u''.join(timer_text_list))
        else:
            timer_datetime = datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)
            result = timer_datetime.strftime('%H:%M')
        return result

if __name__ == "__main__":
    import settings
    botname = 'timer bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(TimerHandler(botname))
    bslack.start_rtm()
