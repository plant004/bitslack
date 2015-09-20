# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
from city_list import CityList

WEATHER_API_URL_BASE = "http://weather.livedoor.com/forecast/webservice/json/v1"
KEY_CITY = u'city'


class WeatherUtils(object):

    DATE_LABEL_LIST = [u'今日', u'明日', u'明後日']

    @classmethod
    def _get_page(cls, url):
        result = None
        try:
            req = urllib2.Request(url)
            
            response = urllib2.urlopen(req)
            result = response.read()
        except Exception, e:
            print e
        return result
    
    @classmethod
    def search_date_label(cls, text):
        result = None
        for dateLabel in cls.DATE_LABEL_LIST:
            if dateLabel in text:
                result = dateLabel
                break
        return result
 
    @classmethod
    def search_city_name(cls, text, default=u'札幌'):
        result = default
        city_name_list = CityList.get_city_name_list()
        for city_name in city_name_list:
            if city_name in text:
                result = city_name
                break
        return result
 
    @classmethod
    def get_weather_info(cls, city_name):
        result = WeatherInfo('', {})
        params = []
        city = CityList.get_city_id(city_name)
        params.append((KEY_CITY, city))
        query_str = urllib.urlencode(params)
        url = '%s?%s' % (WEATHER_API_URL_BASE, query_str)
        #print url
        page = WeatherUtils._get_page(url)
        weather_dict = json.loads(page)
        result = WeatherInfo(city_name, weather_dict)
        return result
    
class WeatherInfo(object):
    def __init__(self, city_name, weather_dict):
        self.city_name = city_name
        self.description = ''
        self.copyright = {}
        self.title = ''
        self.forecasts = []
        if 'title' in weather_dict:
            self.title = weather_dict['title']
        if 'forecasts' in weather_dict:
            for forecast in weather_dict['forecasts']:
                f = {}
                self.set_data(forecast, f, ['dateLabel',], 'dateLabel')
                self.set_data(forecast, f, ['date',], 'date')
                self.set_data(forecast, f, ['telop',], 'telop')
                self.set_data(forecast, f, ['image', 'url',], 'image_url')
                self.set_data(forecast, f, ['temperature', 'min', 'celsius',], 'temperature_min')
                self.set_data(forecast, f, ['temperature', 'max', 'celsius',], 'temperature_max')
                #self.dump(forecast)
                #self.dump(f)
                self.forecasts.append(f)
        if 'description' in weather_dict:
            if 'text' in weather_dict['description']:
                self.description = weather_dict['description']['text']
        if 'copyright' in weather_dict:
            self.copyright = weather_dict['copyright']

    def set_data(self, from_dict, to_dict, from_keys, to_key):
        d = from_dict
        for from_key in from_keys[:-1]:
            if d is not None and from_key in d:
                d = d[from_key]
        #print d
        if d is not None and from_keys[-1] in d:
            to_dict[to_key] = d[from_keys[-1]]
        else:
            to_dict[to_key] = ''
                
    def to_string(self):
       result = u''
       texts = []
       texts.append(self.title)
       for forecast in self.forecasts:
           texts.append(self.format(forecast))
       texts.append(self.description)
       result = u"\n".join(texts)
       return result

    def format(self, f):
        result = u''
        texts = []
        texts.append(u'%sの%s(%s)の天気:%s' % (self.city_name, f['dateLabel'], f['date'], f['telop']))
        if f['temperature_min'] != '' or f['temperature_max'] != '':
            temp_min = ''
            temp_max = ''
            if f['temperature_min'] != '':
                temp_min = u'%s℃' % (f['temperature_min'])
            if f['temperature_max'] != '':
                temp_max = u'%s℃' % (f['temperature_max'])
            texts.append(u'気温:%s～%s' % (temp_min, temp_max))
        result = u' '.join(texts)
        return result

    def get_forecast(self, dateLabel):
        for forecast in self.forecasts:
            if dateLabel == forecast['dateLabel']:
                return forecast
        return None

    def get_forecast_text(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            return self.format(f)
        return ''

    def get_forecast_image_url(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            return f['image_url']

    def get_forecast_telop(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            return f['telop']
        return None
        
    def get_forecast_temp_text(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            if f['temperature_max'] != '':
                temp_max = float(f['temperature_max'])
                if temp_max >= 35:
                    return u'猛暑日'
                elif temp_max >= 30:
                    return u'真夏日'
                elif temp_max >= 25:
                    return u'夏日'
                elif temp_max < 0:
                    return u'真冬日'
            if f['temperature_min'] != '':
                temp_min = float(f['temperature_min'])
                if temp_min < 0:
                    return u'冬日'
        return None
    def get_forecast_is_hot(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            if f['temperature_max'] != '':
                temp_max = float(f['temperature_max'])
                if temp_max >= 25:
                    return True
            if f['temperature_min'] != '':
                temp_min = float(f['temperature_min'])
                if temp_min >= 25:
                    return True
        return False

    def get_forecast_is_cold(self, dateLabel):
        f = self.get_forecast(dateLabel)
        if f is not None:
            if f['temperature_max'] != '':
                temp_max = float(f['temperature_max'])
                if temp_max <= 0:
                    return True
            if f['temperature_min'] != '':
                temp_min = float(f['temperature_min'])
                if temp_min <= 0:
                    return True
        return False
        
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
    text = u'東京の明日の天気'
    city_name = WeatherUtils.search_city_name(text)
    print city_name
    dateLabel = WeatherUtils.search_date_label(text)
    print dateLabel
    weather_info = WeatherUtils.get_weather_info(city_name)
    print weather_info.to_string()
    print weather_info.get_forecast_telop(dateLabel)
    print weather_info.get_forecast_image_url(dateLabel)
    
    weather_info.forecasts[1]['temperature_max'] = '15'
    weather_info.forecasts[1]['temperature_min'] = '0'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_min'] = '-1'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '-1'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '-1'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_min'] = '0'
    weather_info.forecasts[1]['temperature_max'] = '24'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '25'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '29'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '30'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '34'
    print weather_info.get_forecast_temp_text(dateLabel)
    weather_info.forecasts[1]['temperature_max'] = '35'
    print weather_info.get_forecast_temp_text(dateLabel)
