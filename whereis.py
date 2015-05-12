# -*- coding: utf-8 -*-

import datetime
import re
import thread
import time
from bitslack import BitSlack, EventHandler
from pickle_utils import load, save

class WhereIsHandler(EventHandler):
    start_time = None
    debug = True
    file_path = 'whereis.txt'

    def on_hello(self, bitslack_obj, event):
        bitslack_obj.talk(u'起動しました', '#test')
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if float(event['ts']) > self.start_time and \
            '<@USLACKBOT>' in event['text']:
            if self.debug:
                print event['text']
            text = event['text']
            if u'whereis' in text:
                self._on_whereis(bitslack_obj, event)
            elif u'wherearewe' in text:
                self._on_wherearewe(bitslack_obj, event)
            elif u'imat' in text:
                self._on_imat(bitslack_obj, event)
            elif u'botat' in text:
                self._on_botat(bitslack_obj, event)
            elif u'exit' in text:
                bitslack_obj.talk(u'終了します', event['channel'])
                bitslack_obj.end_rtm()

    def _on_whereis(self, bitslack_obj, event):
        user_list = self._parse_user_list(event['text'])
        whereis_data = load(self.file_path)
        texts = []
        userid = u'<@%s>' % (event['user'])
        texts.append(u'%s:' % userid)
        for user in user_list:
            if user in whereis_data:
                texts.append(u'%sさんは %s にいます。' % (user, whereis_data[user]))
            else:
                texts.append(u'%sさんの居場所はわかりません。' % (user))
        bitslack_obj.talk(texts, event['channel'], botname=self.name)

    def _on_wherearewe(self, bitslack_obj, event):
        users = bitslack_obj.get_users()
        whereis_data = load(self.file_path)
        texts = []
        print whereis_data
        userid = u'<@%s>' % (event['user'])
        texts.append(u'%s:' % userid)
        for username, user_info in users.items():
            user = u'<@%s>' % (user_info['id'])
            if user in whereis_data:
                texts.append(u'%sさんは %s にいます。' % (user, whereis_data[user]))
            else:
                texts.append(u'%sさんの居場所はわかりません。' % (user))
        bitslack_obj.talk(texts, event['channel'], botname=self.name)

    def _parse_user_list(self, text):
        result = []
        text = re.sub(r'<@USLACKBOT>:?', '', text, count=1)
        result = re.findall('(<@.*?>)', text)
        return result

    def _on_imat(self, bitslack_obj, event):
        where = self._parse_where(event['text'], u'imat')
        texts = []
        userid = u'<@%s>' % (event['user'])
        whereis_data = load(self.file_path)
        old_where = None
        if userid in whereis_data:
            old_where = whereis_data[userid]
        whereis_data[userid] = where
        save(whereis_data, self.file_path)
        if old_where is not None:
            texts.append(u'%s: 居場所を変更しました。(%s -> %s)' % (userid, old_where, where))
        else:
            texts.append(u'%s: 居場所を設定しました。(%s)' % (userid, where))
        bitslack_obj.talk(texts, event['channel'], botname=self.name)

    def _on_botat(self, bitslack_obj, event):
        where = self._parse_where(event['text'], u'botat')
        texts = []
        userid = u'<@%s>' % (event['user'])
        botid = u'<@USLACKBOT>'
        whereis_data = load(self.file_path)
        old_where = None
        if botid in whereis_data:
            old_where = whereis_data[botid]
        whereis_data[botid] = where
        save(whereis_data, self.file_path)
        if old_where is not None:
            texts.append(u'%s: %sの居場所を変更しました。(%s -> %s)' % (userid, botid, old_where, where))
        else:
            texts.append(u'%s: %sの居場所を設定しました。(%s)' % (userid, botid, where))
        bitslack_obj.talk(texts, event['channel'], botname=self.name)

    def _parse_where(self, text, prefix):
        result = ''
        where_list = re.findall(u'%s (.*)' % (prefix), text)
        if len(where_list) > 0:
            result = where_list[0]
        return result
        
if __name__ == "__main__":
    import settings
    bslack = BitSlack(settings.SLACK_API_KEY, settings.SLACK_BOT_NAME,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(WhereIsHandler('whereis bot'))
    bslack.start_rtm()
