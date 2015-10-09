# -*- coding: utf-8 -*-

import datetime
import random
import time
import thread
from bitslack import BitSlack
from event_handler import BotHandler
from weather_hacks.city_list import CityList 
from weather_hacks.weather_utils import WeatherUtils

class ForecastHandler(BotHandler):
    SCHEDULED_CITY_LIST = [
        u'東京',
        u'札幌',
    ]

    def __init__(self, name=None):
        BotHandler.__init__(self, name)
        respond_patterns = [
            ([u'天気',u'weather'], self.forecast),
            #([u'予報地域一覧',u'report_list'], self.forecast),
        ]
        self.set_respond_patterns(respond_patterns)
        self.set_debug(False)

    def on_hello(self, bitslack_obj, event):
        BotHandler.on_hello(self, bitslack_obj, event)
        def timer_thread(*args):
            while self.thread_id == thread.get_ident():
                time.sleep(1)
                now = datetime.datetime.now()
                if now.weekday() < 5:
                    morning = datetime.datetime(now.year, now.month, now.day, 7, 30, 0)
                    evening = datetime.datetime(now.year, now.month, now.day, 18, 30, 0)
                    is_morning = abs(now - morning) < datetime.timedelta(seconds=1)
                    is_evening= abs(now - evening) < datetime.timedelta(seconds=1)
                    if is_morning:
                        for city in ForecastHandler.SCHEDULED_CITY_LIST:
                            event = {
                                u'text': u'今日の%sの天気' % (city),
                                u'channel': u'#weatherreport',
                            }
                            self.forecast(bitslack_obj, event, args=())
                    if is_evening:
                        for city in ForecastHandler.SCHEDULED_CITY_LIST:
                            event = {
                                u'text': u'明日の%sの天気' % (city),
                                u'channel': u'#weatherreport',
                            }
                            self.forecast(bitslack_obj, event, args=())
        self.thread_id = thread.start_new_thread(timer_thread, ())

    def forecast(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return None
        city_name = WeatherUtils.search_city_name(event['text'], None)
        if city_name is not None:
            weather_info = WeatherUtils.get_weather_info(city_name)
            dateLabel = WeatherUtils.search_date_label(event['text'])
            if dateLabel is not None:
                result = []
                forecast = weather_info.get_forecast_text(dateLabel)
                result.append(forecast)
                temp_text = weather_info.get_forecast_temp_text(dateLabel)
                if temp_text is not None:
                    extra_temp_text = u''
                    if weather_info.get_forecast_is_hot(dateLabel):
                        hot_texts = [
                            u'',
                            u'暑いので熱中症に気をつけてください。',
                            u'暑いので熱中症に気をつけて、小まめに水分補給をするようにしましょう。',
                            u'アイスを食べたいですね。',
                        ]
                        random.shuffle(hot_texts)
                        extra_temp_text = hot_texts[0]
                    elif weather_info.get_forecast_is_cold(dateLabel):
                        cold_texts = [
                            u'',
                            u'寒いので風邪をひかないよう気をつけてください。',
                            u'寒いので風邪をひかないよう、暖かい服装を心がけましょう。',
                            u'寒いのでストーブの前で温まっていたいですね。',
                        ]
                        random.shuffle(cold_texts)
                        extra_temp_text = cold_texts[0]
                    temp_message = u'%sだそうです。%s' % (temp_text, extra_temp_text)
                    result.append(temp_message)
                telop = weather_info.get_forecast_telop(dateLabel)
                if u'雨' in telop:
                    notice = u'%sは雨が降るようなので、傘を忘れないで下さいね。' % (dateLabel)
                    result.append(notice)
                elif u'雪' in telop:
                    notice = u'%sは雪が降るようなので、足元や交通機関の遅れに気をつけて下さいね。' % (dateLabel)
                    result.append(notice)
                elif telop == u'晴れ':
                    notice = u'%sは一日良い天気みたいですよ！' % (dateLabel)
                    result.append(notice)
                boticon = weather_info.get_forecast_image_url(dateLabel)
                self.talk(bitslack_obj, result, event, boticon=boticon)
                return None
            else:
                result = weather_info.to_string()
        else:
            result = u'ごめんなさい、天気予報を取得する地域が認識できませんでした。'
        return result


if __name__ == "__main__":
    import settings
    botname = u'forecast bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(ForecastHandler(botname))
    bslack.start_rtm()
