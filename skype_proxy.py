# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import datetime
import re
import thread
import time
from skype_helper import SkypeHelper
from bitslack import BitSlack
from event_handler import BotHandler

# このProxyはP2Pチャット（/createmoderatedchatで作成したグループチャット）にのみ対応しています。
# クラウドベースの現在のチャットには使用できません。
# TODO: 複数チャンネル対応
class Skype2Slack(SkypeHelper):

    def __init__(self):
        SkypeHelper.__init__(self)
        self.bs = None
        self.enable = True

    def set_bitslack_obj(self, bitslack_obj):
        self.bs = bitslack_obj

    def set_enable(self, enable):
        self.enable = enable

    def get_channels(self, chat_name):
        result = []
        for e in settings.SKYPE_CHAT_CHANNEL_LIST:
            if e[0] == chat_name:
                result.append(e[1])
        return result

    def send_message_to_slack(self, message):
        if self.bs is not None and \
                self.enable:
            text = message.Body
            if text.find('@skype:') == -1 and text.find('@slack:') == -1:
                sender_display_name = message.FromDisplayName
                prefix = u'from %s@skype:' % (sender_display_name)
                texts = [prefix, text]
                channels = self.get_channels(message.Chat.Name)
                for channel in channels:
                    self.bs.talk(texts, channel)

    def on_message_sent(self, message): 
        self.send_message_to_slack(message)

    def on_message_received(self, message):
        self.send_message_to_slack(message)

class SkypeProxy(BotHandler):

    TO_SKYPE = u'^(.*)$'
    ENABLE_SKYPE = u'enable_skype$'
    DISABLE_SKYPE = u'disable_skype$'

    def __init__(self, name=None):
        BotHandler.__init__(self, name, hear_on_respond=False)
        self.enable = True
        self.s2s = Skype2Slack()
        respond_patterns = [
            ((SkypeProxy.ENABLE_SKYPE,), self.enable_skype),
            ((SkypeProxy.DISABLE_SKYPE,), self.disable_skype),
        ]
        hear_patterns = [
            ((SkypeProxy.TO_SKYPE,), self.to_skype),
        ]
        self.set_respond_patterns(respond_patterns)
        self.set_hear_patterns(hear_patterns)

    def set_enable(self, enable):
        self.enable = enable
        self.s2s.set_enable(enable)

    def get_chat_names(self, channel_name):
        result = []
        for e in settings.SKYPE_CHAT_CHANNEL_LIST:
            if e[1] == channel_name:
                result.append(e[0])
        return result

    def on_hello(self, bitslack_obj, event):
        self.bs = bitslack_obj
        self.s2s.set_bitslack_obj(bitslack_obj)
#        def run(*args):
#            while self.thread_id == thread.get_ident():
#                input('')
#        self.thread_id = thread.start_new_thread(run, ())


    def to_skype(self, bitslack_obj, event, args):
        if event['text'].find('@skype:') == -1 and \
                event['text'].find('@slack:') == -1 and \
                self.enable:
            user_name = bitslack_obj.get_user_name_by_id(event['user'])
            prefix = u'from %s@slack:' % (user_name)
            text_list = [prefix, ] + event['text'].split(u"\n")
            message = u"\n".join(text_list)
            channel_name = bitslack_obj.get_channel_name_by_id(event['channel'], with_sharp=True)
            chat_names = self.get_chat_names(channel_name)
            for chat_name in chat_names:
                chat = self.s2s.get_chat_by_name(chat_name)
                self.s2s.send_message(message, chat)
        return None

    def enable_skype(self, bitslack_obj, event, args):
        self.set_enable(True)
        return u'SkypeProxyを有効化しました。'

    def disable_skype(self, bitslack_obj, event, args):
        self.set_enable(False)
        return u'SkypeProxyを無効化しました。'

if __name__ == "__main__":
    import settings
    botname = 'skype proxy'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(SkypeProxy(botname))
    bslack.start_rtm()
