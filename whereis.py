# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import datetime
import re
import thread
import time
from bitslack import BitSlack
from event_handler import BotHandler
from pickle_utils import load, save

class WhereIsHandler(BotHandler):
    file_path = 'whereis.txt'

    def __init__(self, name=None):
        BotHandler.__init__(self, name)
        description = u'居場所を設定します。'.encode('utf-8')
        respond_patterns = [
            ([u'where_is',], self._on_where_is),
            ([u'im_at',], self._on_im_at),
            ([u'bot_at',], self._on_bot_at),
            ([u'where_are_we',], self._on_where_are_we),
        ]
        self.set_respond_patterns(respond_patterns)
        self.parser = ArgumentParser(description=description, prog=u'@slackbot where_is|im_at|bot_at|where_are_we'.encode('utf-8'), add_help=False)

        self.parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))

        self.parser.add_argument('user', help=u'ユーザID(@slackbotなど)'.encode('utf-8'))
        self.parser.add_argument('place', help=u'場所(im_at, bot_atのみ)'.encode('utf-8'))

    def _help(self, bitslack_obj, event, args):
        result = None
        text_list = event['text'].split()
        args, unknown_args = self.parser.parse_known_args(text_list)
        if args.usage:
            usage = self.parser.format_help()
            result = usage.decode('utf-8')
        return result

    def _on_where_is(self, bitslack_obj, event, args):
        help = self._help(bitslack_obj, event, args)
        if help is not None:
            return help
        user_list = self._parse_user_list(event['text'])
        not_user_list = self._parse_not_user_list(event['text'])
        whereis_data = load(self.file_path)
        texts = []
        userid = u'<@%s>' % (event['user'])
        texts.append(u'%s:' % userid)
        for user in user_list:
            if user in whereis_data:
                texts.append(u'%sさんは %s にいます。' % (user, whereis_data[user]))
            else:
                texts.append(u'%sさんの居場所はわかりません。' % (user))
        for not_user in not_user_list:
            texts.append(u'%sさんは多分このチームに所属していません。' % (not_user))
        return texts

    def _on_where_are_we(self, bitslack_obj, event, args):
        help = self._help(bitslack_obj, event, args)
        if help is not None:
            return help
        users = bitslack_obj.get_users()
        whereis_data = load(self.file_path)
        texts = []
        userid = u'<@%s>' % (event['user'])
        for username, user_info in users.items():
            user = u'<@%s>' % (user_info['id'])
            if user in whereis_data:
                texts.append(u'%sさんは %s にいます。' % (user, whereis_data[user]))
            else:
                texts.append(u'%sさんの居場所はわかりません。' % (user))
        return texts

    def _parse_user_list(self, text):
        result = []
        text = re.sub(r'<@USLACKBOT>:?', '', text, count=1)
        result = re.findall(r'(<@.*?>)', text)
        return result

    def _parse_not_user_list(self, text):
        result = []
        text = re.sub(r'<@USLACKBOT>:?', '', text, count=1)
        result = re.findall(r'[^<](@[a-zA-Z0-9._-]*)', text)
        return result

    def _on_im_at(self, bitslack_obj, event, args):
        help = self._help(bitslack_obj, event, args)
        if help is not None:
            return help
        where = self._parse_where(event['text'], u'im_at')
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
        return texts

    def _on_bot_at(self, bitslack_obj, event, args):
        help = self._help(bitslack_obj, event, args)
        if help is not None:
            return help
        where = self._parse_where(event['text'], u'bot_at')
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
        return texts

    def _parse_where(self, text, prefix):
        result = ''
        where_list = re.findall(u'%s (.*)' % (prefix), text)
        if len(where_list) > 0:
            result = where_list[0]
        return result
        
if __name__ == "__main__":
    import settings
    botname = u'whereis bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(WhereIsHandler(botname))
    bslack.start_rtm()
