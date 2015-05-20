# -*- coding: utf-8 -*-

from bitslack import BitSlack

if __name__ == "__main__":
    import settings
    from hello import HelloHandler
    from timer import TimerHandler
    from whereis import WhereIsHandler
    bslack = BitSlack(settings.SLACK_API_KEY, 'multibot',
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(HelloHandler('hello bot'))
    bslack.add_event_handler(TimerHandler('timer bot'))
    bslack.add_event_handler(WhereIsHandler('where is bot'))
    bslack.start_rtm()
