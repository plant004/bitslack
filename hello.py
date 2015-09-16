# -*- coding: utf-8 -*-

from bitslack import BitSlack
from event_handler import BotHandler

class HelloHandler(BotHandler):

    def __init__(self, name=None):
        BotHandler.__init__(self, name)
        respond_patterns = [
            ([u'.*',], self.hello),
        ]
        self.set_respond_patterns(respond_patterns)
        hear_patterns = [
            ([u'[Hh]ello',], self.hello),
        ]
        self.set_hear_patterns(hear_patterns)
        self.set_debug(False)

    def hello(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        user_str = self.get_event_user_str(event)
        result = u'Hello, %s.' % (user_str)
        return result

if __name__ == "__main__":
    import settings
    botname = u'hello bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(HelloHandler(botname))
    bslack.start_rtm()
