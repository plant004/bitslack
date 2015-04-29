# -*- coding: utf-8 -*-
"""
    BitSlack
    Slackerを使ったSlackボット用クラスのスクリプトです。
"""

import datetime
import time
from slacker import Slacker


class BitSlack(object):
    """
        BitSlack
        Slackerを使ったSlackボット用クラスです。

        Attributes:
            LINES_PER_POST: 投稿当りの行数
            SLEEP_PER_POST: 投稿当りのスリープ秒数

    """

    LINES_PER_POST = 20
    SLEEP_PER_POST = 1
    
    def __init__(self, slack_api_key, botname, boticon,
                lines_per_post=LINES_PER_POST, sleep_per_post=SLEEP_PER_POST, debug=False):
        """
            コンストラクタです。
            :type slack_api_key: str
            :param slack_api_key: APIキー
        """
        self.slacker = Slacker(slack_api_key)
        self.botname = botname
        self.boticon = boticon
        self.lines_per_post = lines_per_post
        self.sleep_per_post = sleep_per_post
        self.users = self.get_users()
        self.debug = debug

    def get_users(self):
        result = {}
        response = self.slacker.users.list()
        if 'members' in response.body:
            for member in response.body['members']:
                username = member['name']
                result[username] = member
        return result

    def get_user(self, username):
        result = {}
        if self.users is None or username not in self.users:
            self.users = self.get_users()
        if username in self.users:
            result = self.users[username]
        return result
                
    def get_user_property(self, username, key):
        result = None
        user = self.get_user(username)
        if key in user:
            result = user[key]
        return result
                
    def get_user_real_name(self, username):
        result = self.get_user_property(username, 'real_name') 
        if result is None or result == '':
            result = username
        return result 

    def get_dm_channel(self, username):
        return self.get_user_property(username, 'id')

    def _slice_texts(self, texts):
        if isinstance(texts, str):
            texts = (texts,)
        total_line_num = len(texts)
        for i in range(total_line_num % self.lines_per_post):
            result = None
            start = i * self.lines_per_post
            end = start + self.lines_per_post
            end = total_line_num if end > total_line_num else end
            result = texts[start:end]
            yield result

    def talk(self, texts, to='#random', botname=None, boticon=None):
        # channel
        channel = to
        if not channel.startswith('#'):
            channel = self.get_dm_channel(channel)

        # username
        username = botname
        if username is None:
            username = self.botname

        # icon_url
        icon_url = boticon
        if icon_url is None:
            icon_url = self.boticon

        # post
        for post_texts in self._slice_texts(texts):
            text = None
            if len(post_texts) > 0:
                text = u"\n".join(post_texts)
                if self.debug:
                    print text
                self.slacker.chat.post_message(channel, text, username, icon_url=icon_url)
            if self.sleep_per_post > 0:
                time.sleep(self.sleep_per_post)

    def start_rtm(self):
        response = self.slacker.rtm.start()
        if self.debug:
            self.dump(response.body)

    def dump(self, data, name=None, indent=0):
        spaces = ''.join([' ' * indent])
        if isinstance(data, list):
            if name is not None:
                print "%s%s:" % (spaces, name)
            for i, v in enumerate(data):
                self.dump(v, i, indent=indent+4)
        elif isinstance(data, dict):
            if name is not None:
                print "%s%s:" % (spaces, name)
            for k, v in data.items():
                self.dump(v, k, indent=indent+4)
        else:
            print (u"%s%s:%s" % (spaces, name, data)).encode('utf-8')

if __name__ == "__main__":
    import settings
    bslack = BitSlack(settings.SLACK_API_KEY,
            settings.SLACK_BOT_NAME,
            settings.SLACK_ICON_URL,
            debug=True)
    bslack.talk(('test', 'hello slack'), '#test')
    #bslack.start_rtm()
