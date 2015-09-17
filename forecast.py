# -*- coding: utf-8 -*-

from bitslack import BitSlack
from event_handler import BotHandler
from weather_hacks.city_list import CityList 
from weather_hacks.weather_utils import WeatherUtils

class ForecastHandler(BotHandler):

    def __init__(self, name=None):
        BotHandler.__init__(self, name)
        respond_patterns = [
            ([u'天気',u'weather'], self.forecast),
            ([u'予報地域一覧',u'report_list'], self.forecast),
        ]
        self.set_respond_patterns(respond_patterns)
        self.set_debug(False)

    def forecast(self, bitslack_obj, event, args):
        print 'forecast'
        if self.is_bot(event):
            return None
        city_name = WeatherUtils.search_city_name(event['text'], None)
        if city_name is not None:
            weather_info = WeatherUtils.get_weather_info(city_name)
            dateLabel = WeatherUtils.search_date_label(event['text'])
            if dateLabel is not None:
                result = weather_info.get_forecast_text(dateLabel)
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
