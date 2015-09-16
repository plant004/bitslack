# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import re
from bitslack import BitSlack
from event_handler import BotHandler

class DoppelHandler(BotHandler):
    
    DOPPEL_PATTERNS = [
        u'doppel',
    ]
    def __init__(self, name, original_name):
        BotHandler.__init__(self, name)
        description = u'本人に成りすまして物まねをします。'.encode('utf-8')
        self.after_fake = False
        self.original_name = original_name
        self.original_user = None
        self.original_icon = None
        self.original_mension = None
        respond_patterns = [
            (DoppelHandler.DOPPEL_PATTERNS, self.fake),
        ]
        self.set_respond_patterns(respond_patterns)
        self.parser = ArgumentParser(description=description, prog=u'@slackbot doppel'.encode('utf-8'), add_help=False)

        self.parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))

        self.parser.add_argument('user', help=u'なり替わるユーザ(@user)'.encode('utf-8'))

    def on_hello(self, bitslack_obj, event):
        BotHandler.on_hello(self, bitslack_obj, event)
        self.init_original_info(bitslack_obj)
        self._update_immitate_patterns()

    def on_user_change(self, bitslack_obj, event):
        self.original_name = event['user']['name']
        self.original_user = event['user']
        self.original_icon = self._get_icon()
        self.original_mension = u'<@%s>' % (self.original_user['id'])
        self._update_immitate_patterns()
        bitslack_obj.dump(event)

    def fake(self, bitslack_obj, event, args):
        text_list = event['text'].split()
        args, unknown_args = self.parser.parse_known_args(text_list)
        if args.usage:
            usage = self.parser.format_help()
            return usage.decode('utf-8')
        original_name = self._get_username(bitslack_obj, event['text'])
        self.init_original_info(bitslack_obj, original_name)
        text = u'%sさんになりすましました。' % (self.original_mension)
        self._update_immitate_patterns()
        self.talk_as_original(bitslack_obj, text, event['channel'])
        self.after_fake = True
        return None

    def _update_immitate_patterns(self):
        hear_patterns = [
            (
                self._make_immitate_patterns(), 
                self.immitate
            ),
        ]
        self.set_hear_patterns(hear_patterns)

    def _exists(self, key, dict_data):
        return key in dict_data and dict_data[key] != ''

    def _make_immitate_patterns(self):
        result = []
        if self.original_mension:
            result.append(self.original_mension)
        if self._exists('profile', self.original_user):
            profile = self.original_user['profile']
            if self._exists('real_name', profile):
                result.append(self.original_user['profile']['real_name'])
            if self._exists('real_name_normalized', profile):
                result.append(self.original_user['profile']['real_name_normalized'])
            if self._exists('last_name', profile):
                result.append(self.original_user['profile']['last_name'])
            if self._exists('first_name', profile):
                result.append(self.original_user['profile']['first_name'])
            if self._exists('skype', profile):
                result.append(self.original_user['profile']['skype'])
        if self._exists('name', self.original_user):
            result.append(self.original_user['name'])
        return result

    def immitate(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        if not self.after_fake:
            userid = '<@%s>' % (event['user'])
            text = re.sub(args[0], '', event['text'])
            self.talk_as_original(bitslack_obj, text, event['channel'])
        self.after_fake = False
        return None

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
            if 'profile' in self.original_user:
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
    original = 'plant004' # target user name
    channel = '#test'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    handler = DoppelHandler(botname, original)
    handler.init_original_info(bslack)
    handler.talk_as_original(bslack, u'hello', channel)
    
    bslack.add_event_handler(handler)
    bslack.start_rtm()
