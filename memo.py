# -*- coding: utf-8 -*-

import datetime
import re
import thread
import time
from bitslack import BitSlack
from event_handler import BotHandler
from pickle_utils import load, save

class MemoHandler(BotHandler):
    start_time = None
    debug = True
    file_path = 'memo.txt'

    def __init__(self, name=None):
        BotHandler.__init__(self, name, hear_on_respond=False)
        respond_patterns = [
            ([u' lsmemo',], self.lsmemo),
            ([u' mkmemo ([^ ]+) (.+)$', u' mkmemo',], self.mkmemo),
            ([u' catmemo ([^ ]+)$', u' catmemo',], self.catmemo),
            ([u' rmmemo ([^ ]+)$', u' rmmemo',], self.rmmemo),
        ]
        self.memo_data = load(self.file_path)
        self.set_respond_patterns(respond_patterns)
        self.set_debug(False)

    def lsmemo(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        user_str = self.get_event_user_str(event)
        texts = []
        keys = self.memo_data.keys()
        if len(keys) > 0:
            texts.append(u'%s メモリスト:' % user_str)
            for key in keys:
                texts.append(key)
            return texts
        else:
            texts.append(u'%s メモは現在ありません。' % user_str)
            return texts
        return None

    def mkmemo(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        user_str = self.get_event_user_str(event)
        if len(args[0][0]) > 1 and isinstance(args[0][0], tuple):
            key = args[0][0][0]
            value = args[0][0][1]
            texts = u'%s メモ %s を更新しました。' % (user_str, key)
            if key in self.memo_data:
                texts = u'%s メモ %s を作成しました。' % (user_str, key)
            self.memo_data[key] = value
            save(self.memo_data, self.file_path)
            return texts 
        return u'引数が足りません。'

    def catmemo(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        user_str = self.get_event_user_str(event)
        if len(args) > 1 and isinstance(args, list):
            key = args[0][0]
            if key != u'':
                texts = u'%s メモ %s はありません。' % (user_str, key)
                if key in self.memo_data:
                    texts = u'%s' % self.memo_data[key]
                return texts 
        return u'引数が足りません。'
        
    def rmmemo(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        user_str = self.get_event_user_str(event)
        if len(args) > 1 and isinstance(args, list):
            key = args[0][0]
            texts = u'%s メモ %s はありません。' % (user_str, key)
            if key in self.memo_data:
                del self.memo_data[key]
                save(self.memo_data, self.file_path)
                texts = u'%s メモ %s を削除しました。' % (user_str, key)
            return texts 
        return u'引数が足りません。'
        
if __name__ == "__main__":
    import settings
    botname = u'memo bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(MemoHandler(botname))
    bslack.start_rtm()
