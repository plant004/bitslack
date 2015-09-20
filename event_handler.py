# -*- coding: utf-8 -*-

import time
import types
import re

class EventHandler(object):
    debug = False
    """
        シンプルなイベントハンドラクラスです。  
    """
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        else:
            self.name = str(id(self))

    def set_debug(self, debug):
        self.debug = debug

    def on_event(self, bitslack_obj, event):
        """
            Slackイベント発生時に呼ばれるメソッドです。
            必要に応じて実装し、BitSlackのadd_event_handler()メソッドでハンドラを追加してください。
        """
        if 'type' in event:
            event_type = event['type']
            handle_method_name = 'on_%s' % event_type
            if hasattr(self, handle_method_name):
                handle_method = getattr(self, handle_method_name)
                handle_method(bitslack_obj, event)

    def on_hello(self, bitslack_obj, event):
        """
            helloイベントを受信した時に呼ばれるメソッドです。
        """
        if self.debug:
            bitslack_obj.talk('on_hello called', to='#test', botname=self.name)

class BotHandler(EventHandler):
    """
        Bot用のイベントハンドラクラスです。  
    """
    start_time = None

    def __init__(self, name=None):
        EventHandler.__init__(self, name)
        # pattern format: list of tupple ([expr string sequence], response string or function)
        # function must receives lack event dict and result of re.findall(); then return string
        # パターンフォーマット: ([表現文字列のシーケンス], レスポンス文字列または文字列を返す関数)のタプルのリスト
        # 関数は slackイベント辞書とre.findall()の結果を受け取り、文字列を返して下さい。
        self.respond_patterns = []
        self.hear_patterns = []
        self.start_time = None

    def set_respond_patterns(self, patterns):
        self.respond_patterns = patterns

    def set_hear_patterns(self, patterns):
        self.hear_patterns = patterns

    def get_respond_patterns(self):
        return self.respond_patterns

    def get_hear_patterns(self):
        return self.hear_patterns

    def add_respond_pattern(self, pattern):
        self.respond_patterns.append(pattern)

    def add_hear_pattern(self, pattern):
        self.hear_patterns.append(pattern)

    def remove_respond_pattern(self, pattern):
        self.respond_patterns.remove(pattern)

    def remove_hear_pattern(self, pattern):
        self.hear_patterns.remove(pattern)

    def clear_respond_patterns(self):
        self.respond_patterns = []

    def clear_hear_patterns(self):
        self.hear_patterns = []

    def on_hello(self, bitslack_obj, event):
        EventHandler.on_hello(self, bitslack_obj, event)
        self.start_time = time.time()

    def on_message(self, bitslack_obj, event):
        if self.is_after_boot(event):
            if self.is_called(event):
                self._respond(bitslack_obj, event)
            self._hear(bitslack_obj, event)

    def _respond(self, bitslack_obj, event):
        self._match_and_response(bitslack_obj, event,self.respond_patterns)

    def _hear(self, bitslack_obj, event):
        self._match_and_response(bitslack_obj, event,self.hear_patterns)
  
    def _match_and_response(self, bitslack_obj, event, patterns_and_response):
        for patterns_and_response in patterns_and_response:
            patterns = patterns_and_response[0]
            response = patterns_and_response[1]
            response_type = type(response)
            if  response_type is types.FunctionType or response_type is types.MethodType:
                args = []
                for pattern in patterns:
                    find_result = re.findall(pattern, event['text'])
                    args.extend(find_result)
                try:
                    if len(args) > 0:
                        response_text = response(bitslack_obj, event, args)
                        if response_text is not None:
                            #print 'function response'
                            self.talk(bitslack_obj, response_text, event)
                except Exception, e:
                    print e
            else:
                response_text = response
                for pattern in patterns:
                    find_result = re.findall(pattern, event['text'])
                    if find_result:
                        #print 'string response'
                        self.talk(bitslack_obj, response_text, event)
                        break
  
    def is_after_boot(self, event):
        return float(event['ts']) > self.start_time

    def is_bot(self, event):
        return 'subtype' in event and event['subtype'] == u'bot_message'

    def is_called(self, event):
        return u'<@USLACKBOT>' in event['text']

    def get_event_user_str(self, event):
        result = ''
        if 'user' in event:
            result = '<@%s>' % (event['user'])
        return result

#    def remove_slackbot_id(self, event):
#        result = re.sub(r'<@USLACKBOT>:? *', '', result)
#        return result
#
#    def replace_slackbot_id_to_event_user(self, event):
#        user_str = self.get_event_user_str(event)
#        result = re.sub(r'<@USLACKBOT>', userid, result)
#        return result
#
    def talk(self, bitslack_obj, texts, event, boticon=None):
        self._talk_to_event_channel(bitslack_obj, texts, event, boticon)

    def _talk_to_event_channel(self, bitslack_obj, texts, event, boticon):
        bitslack_obj.talk(texts, event['channel'], botname=self.name, boticon=boticon)

