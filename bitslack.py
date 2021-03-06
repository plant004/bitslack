# -*- coding: utf-8 -*-
"""
    BitSlack
    Slackerを使ったSlackボット用クラスのスクリプトです。
"""

import datetime
import json
import time
import thread
import websocket
from slacker import Slacker
from event_handler import EventHandler
import logging
class DefaultHandler(logging.StreamHandler):
    pass
handler = DefaultHandler()
logging.getLogger().addHandler(handler)

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
                lines_per_post=LINES_PER_POST, sleep_per_post=SLEEP_PER_POST,
                on_message=None, on_error=None, on_open=None, on_close=None,
                debug=False):
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
        self.debug = debug
        self.ws = None
        self.rtm_event_id = 1
        self.init_rtm_funcs(on_message, on_error, on_open, on_close)
        self.users = {}
        self.users = self.get_users()
        time.sleep(1)
        self.channels = {}
        self.channels = self.get_channels()
        self.event_handlers = {}

    def add_event_handler(self, event_handler):
        key = event_handler.name
        self.event_handlers[key] = event_handler

    def remove_event_handler(self, event_handler):
        key = event_handler.name
        if key in self.event_handlers:
            del self.event_handlers[key]

    def on_message_default(self, ws, message):
        if self.debug:
            print message
        event = self.decode_event(message)
        for event_handler_name, event_handler in self.event_handlers.items():
            event_handler.on_event(self, event)
        #ws.close()

    def on_error_default(self, ws, error):
        print error
        ws.close()
        # try reconnect if connection closed error
        if str(error) == "Connection is already closed.":
            self.start_rtm()

    def on_close_default(self, ws):
        if self.debug:
            print "### closed ###"

    def on_open_default(self, ws):
        if self.debug:
            print "### open ###"

    def init_rtm_funcs(self, on_message=None, on_error=None, on_open=None, on_close=None):
        if on_message:
            self.on_message = on_message
        else:
            self.on_message = self.on_message_default

        if on_error:
            self.on_error = on_error
        else:
            self.on_error = self.on_error_default

        if on_open:
            self.on_open = on_open
        else:
            self.on_open = self.on_open_default
            
        if on_close:
            self.on_close = on_close
        else:
            self.on_close = self.on_close_default

    # user functions
    def get_users(self):
        result = self.users
        response = self.slacker.users.list()
        if 'members' in response.body:
            result = self.make_users(response.body['members'])
        return result

    def make_users(self, user_list):
        result = self.users
        for user in user_list:
            username = user['name']
            result[username] = user
        return result

    def get_user(self, username):
        result = {}
        if self.users is None or username not in self.users:
            self.users = self.get_users()
        if username in self.users:
            result = self.users[username]
        return result
                
    def get_user_by_id(self, user_str):
        result = {}
        if self.users is None:
            self.users = self.get_users()
        for user in self.users.values():
            if 'id' in user:
                print user['id']
            if 'id' in user and user['id'] == user_str:
                result = user
                break
        return result
                
    def get_user_property(self, username, key):
        result = None
        user = self.get_user(username)
        if key in user:
            result = user[key]
        return result
                
    def get_user_name_by_id(self, user_id):
        result = ''
        user = self.get_user_by_id(user_id)
        if 'name' in user:
            result = user['name']
        return result

    def get_user_real_name(self, username):
        result = self.get_user_property(username, 'real_name') 
        if result is None or result == '':
            result = username
        return result 

    def get_user_id(self, username):
        return self.get_user_property(username, 'id')

    # channel functions
    def get_channels(self):
        result = self.channels
        response = self.slacker.channels.list()
        if 'channels' in response.body:
            result = self.make_channels(response.body['channels'])
        return result

    def make_channels(self, channel_list):
        result = self.channels
        for channel in channel_list:
            channel_name = channel['name']
            result[channel_name] = channel
        return result

    def get_channel(self, channel_name):
        result = {}
        if self.channels is None or channel_name not in self.channels:
            self.channels = self.get_channels()
        if channel_name in self.channels:
            result = self.channels[channel_name]
        return result

    def get_channel_by_id(self, channel_id):
        result = {}
        if self.channels is None:
            self.channels = self.get_channels()
        for channel_name, channel in self.channels.items():
            if channel['id'] == channel_id:
                result = channel
                break
        return result

    def get_channel_property(self, channel_name, key):
        result = None
        channel = self.get_channel(channel_name)
        if key in channel:
            result = channel[key]
        return result

    def get_channel_property_by_id(self, channel_id, key):
        result = None
        channel = self.get_channel_by_id(channel_id)
        if key in channel:
            result = channel[key]
        return result

    def get_channel_id(self, channel_name):
        return self.get_channel_property(channel_name[1:], 'id')

    def get_channel_name_by_id(self, channel_id, with_sharp=False):
        result = None
        channel_name = self.get_channel_property_by_id(channel_id, 'name')
        if channel_name != None:
            prefix = '#' if with_sharp else ''
            result = '%s%s' % (prefix, channel_name)
        return result

    def get_talk_channel(self, channel_name):
        result = None
        if channel_name.startswith('#'):
           result = self.get_channel_id(channel_name)
        else:
           result = self.get_user_id(channel_name)
        return result 
 
    # post functions
    def _slice_texts(self, texts):
        if isinstance(texts, str) or isinstance(texts, unicode):
            yield (texts, )
        else:
            total_line_num = len(texts)
            for i in range(total_line_num % self.lines_per_post):
                result = None
                start = i * self.lines_per_post
                end = start + self.lines_per_post
                end = total_line_num if end > total_line_num else end
                result = texts[start:end]
                yield result

    def talk(self, texts, to='#random', botname=None, boticon=None, is_rtm=False, as_user=False):
        channel, username, icon_url = self._get_talk_info(to, botname, boticon)
        if is_rtm:
            self._talk_with_rtm_api(texts, channel, username, icon_url, as_user)
        else:
            self._talk_with_web_api(texts, channel, username, icon_url, as_user)

    def _get_talk_info(self, to, botname, boticon):
        result = [None, None, None]
        # channel
        channel = self.get_talk_channel(to)
        if channel is None:
            channel = to
        result[0] = channel
 
        # username
        username = botname
        if username is None:
            username = self.botname
        result[1] = username

        # icon_url
        icon_url = boticon
        if icon_url is None:
            icon_url = self.boticon
        result[2] = icon_url
        return result
        
    def _talk_with_web_api(self, texts, channel, username, icon_url, as_user):
        # post
        for post_texts in self._slice_texts(texts):
            text = None
            if len(post_texts) > 0:
                text = u"\n".join(post_texts)
                if self.debug:
                    print text
                self.slacker.chat.post_message(channel, text, username, icon_url=icon_url, as_user=as_user)
            if self.sleep_per_post > 0:
                time.sleep(self.sleep_per_post)

    def _talk_with_rtm_api(self, texts, channel, username, icon_url, as_user):
        # post
        for post_texts in self._slice_texts(texts):
            text = None
            if len(post_texts) > 0:
                text = u"\n".join(post_texts)
                if self.debug:
                    print text
                type='message'
                event = self._to_json(text, type, channel, username, icon_url, as_user)
                self.ws.send(event)
            if self.sleep_per_post > 0:
                time.sleep(self.sleep_per_post)

    def ping(self):
        event = self._to_json(text=None, type='ping')
        self.ws.send(event)

    def _to_json(self, text=None, type='message', channel=None, username=None, icon_url=None, as_user=None):
        event = {}
        event['id'] = self._get_next_id()
        event['type'] = type
        if type == 'message':
            if text is not None:
                event['text'] = text
            event['channel'] = self.get_channel_id('#random') if channel is None else channel
            if username is not None:
                event['username'] = username
            if icon_url is not None:
                event['icon_url'] = icon_url
            if as_user is not None:
                event['as_user'] = as_user
        #self.dump(event)
        return json.dumps(event, separators=(',',':'))

    def _get_next_id(self):
        result = self.rtm_event_id
        self.rtm_event_id = self.rtm_event_id + 1
        return result

    # rtm functions
    def start_rtm(self):
        response = self.slacker.rtm.start()
        #if self.debug:
        #    self.dump(response.body)
        if 'users' in response.body:
            self.users = self.make_users(response.body['users'])
        if 'channels' in response.body:
            self.channels = self.make_channels(response.body['channels'])
        if 'url' in response.body:
            #websocket.enableTrace(True)
            class KeepaliveHandler(EventHandler):
                def on_hello(self, bitslack_obj, event):
                    def send_ping(*args):
                        while True:
                            time.sleep(60)
                            bitslack_obj.ping()
                    thread.start_new_thread(send_ping, ())
            self.add_event_handler(KeepaliveHandler('_keepalive'))
            self.websocket_url = response.body['url']
            self.ws = websocket.WebSocketApp(self.websocket_url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close)
            self.ws.on_open = self.on_open
            self.ws.run_forever() 

    def end_rtm(self):
        self.ws.close()

    def decode_event(self, message):
        event = {}
        try:
            event = json.loads(message)
        except Exception, e:
            if self.debug:
                print e
            raise e
        return event

    # debug functions
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
    #bslack = BitSlack(settings.SLACK_API_KEY, settings.SLACK_BOT_NAME,
    #        settings.SLACK_ICON_URL,
    #        debug=True)
    #bslack.talk(('test', 'hello slack'), '#test')
    #bslack.talk('test', '#test')
    #bslack.talk(u'test', '#test')
    bslack_rtm = BitSlack(settings.SLACK_API_KEY, settings.SLACK_BOT_NAME,
            settings.SLACK_ICON_URL,
            debug=True)
    class MyEventHandler(EventHandler):
        def on_hello(self, bitslack_obj, event):
            bitslack_obj.talk(('hello from rtm',), '#test', is_rtm=True)
            bitslack_obj.remove_event_handler(self)
            bitslack_obj.add_event_handler(MyEventHandler2('handler2'))
    class MyEventHandler2(EventHandler):
        def on_message(self, bitslack_obj, event):
            bitslack_obj.talk(('bye from trm',), '#test', is_rtm=True)
            bitslack_obj.remove_event_handler(self)
            bitslack_obj.end_rtm()
    bslack_rtm.add_event_handler(EventHandler('bitslack rtm test bot'))
    bslack_rtm.add_event_handler(MyEventHandler('handler1'))
    bslack_rtm.start_rtm()
