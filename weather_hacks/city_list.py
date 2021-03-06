# -*- coding: utf-8 -*-

class CityList(object):
    ID_NAME_MAP = {
        u'011000':u'稚内',
        u'012010':u'旭川',
        u'012020':u'留萌',
        u'013010':u'網走',
        u'013020':u'北見',
        u'013030':u'紋別',
        u'014010':u'根室',
        u'014020':u'釧路',
        u'014030':u'帯広',
        u'015010':u'室蘭',
        u'015020':u'浦河',
        u'016010':u'札幌',
        u'016020':u'岩見沢',
        u'016030':u'倶知安',
        u'017010':u'函館',
        u'017020':u'江差',
        u'020010':u'青森',
        u'020020':u'むつ',
        u'020030':u'八戸',
        u'030010':u'盛岡',
        u'030020':u'宮古',
        u'030030':u'大船渡',
        u'040010':u'仙台',
        u'040020':u'白石',
        u'050010':u'秋田',
        u'050020':u'横手',
        u'060010':u'山形',
        u'060020':u'米沢',
        u'060030':u'酒田',
        u'060040':u'新庄',
        u'070010':u'福島',
        u'070020':u'小名浜',
        u'070030':u'若松',
        u'080010':u'水戸',
        u'080020':u'土浦',
        u'090010':u'宇都宮',
        u'090020':u'大田原',
        u'100010':u'前橋',
        u'100020':u'みなかみ',
        u'110010':u'さいたま',
        u'110020':u'熊谷',
        u'110030':u'秩父',
        u'120010':u'千葉',
        u'120020':u'銚子',
        u'120030':u'館山',
        u'130010':u'東京',
        u'130020':u'大島',
        u'130030':u'八丈島',
        u'130040':u'父島',
        u'140010':u'横浜',
        u'140020':u'小田原',
        u'150010':u'新潟',
        u'150020':u'長岡',
        u'150030':u'高田',
        u'150040':u'相川',
        u'160010':u'富山',
        u'160020':u'伏木',
        u'170010':u'金沢',
        u'170020':u'輪島',
        u'180010':u'福井',
        u'180020':u'敦賀',
        u'190010':u'甲府',
        u'190020':u'河口湖',
        u'200010':u'長野',
        u'200020':u'松本',
        u'200030':u'飯田',
        u'210010':u'岐阜',
        u'210020':u'高山',
        u'220010':u'静岡',
        u'220020':u'網代',
        u'220030':u'三島',
        u'220040':u'浜松',
        u'230010':u'名古屋',
        u'230020':u'豊橋',
        u'240010':u'津',
        u'240020':u'尾鷲',
        u'250010':u'大津',
        u'250020':u'彦根',
        u'260010':u'京都',
        u'260020':u'舞鶴',
        u'270000':u'大阪',
        u'280010':u'神戸',
        u'280020':u'豊岡',
        u'290010':u'奈良',
        u'290020':u'風屋',
        u'300010':u'和歌山',
        u'300020':u'潮岬',
        u'310010':u'鳥取',
        u'310020':u'米子',
        u'320010':u'松江',
        u'320020':u'浜田',
        u'320030':u'西郷',
        u'330010':u'岡山',
        u'330020':u'津山',
        u'340010':u'広島',
        u'340020':u'庄原',
        u'350010':u'下関',
        u'350020':u'山口',
        u'350030':u'柳井',
        u'350040':u'萩',
        u'360010':u'徳島',
        u'360020':u'日和佐',
        u'370000':u'高松',
        u'380010':u'松山',
        u'380020':u'新居浜',
        u'380030':u'宇和島',
        u'390010':u'高知',
        u'390020':u'室戸岬',
        u'390030':u'清水',
        u'400010':u'福岡',
        u'400020':u'八幡',
        u'400030':u'飯塚',
        u'400040':u'久留米',
        u'410010':u'佐賀',
        u'410020':u'伊万里',
        u'420010':u'長崎',
        u'420020':u'佐世保',
        u'420030':u'厳原',
        u'420040':u'福江',
        u'430010':u'熊本',
        u'430020':u'阿蘇乙姫',
        u'430030':u'牛深',
        u'430040':u'人吉',
        u'440010':u'大分',
        u'440020':u'中津',
        u'440030':u'日田',
        u'440040':u'佐伯',
        u'450010':u'宮崎',
        u'450020':u'延岡',
        u'450030':u'都城',
        u'450040':u'高千穂',
        u'460010':u'鹿児島',
        u'460020':u'鹿屋',
        u'460030':u'種子島',
        u'460040':u'名瀬',
        u'471010':u'那覇',
        u'471020':u'名護',
        u'471030':u'久米島',
        u'472000':u'南大東',
        u'473000':u'宮古島',
        u'474010':u'石垣島',
        u'474020':u'与那国島',
    }
    NAME_ID_MAP = {
        u'稚内':u'011000',
        u'旭川':u'012010',
        u'留萌':u'012020',
        u'網走':u'013010',
        u'北見':u'013020',
        u'紋別':u'013030',
        u'根室':u'014010',
        u'釧路':u'014020',
        u'帯広':u'014030',
        u'室蘭':u'015010',
        u'浦河':u'015020',
        u'札幌':u'016010',
        u'岩見沢':u'016020',
        u'倶知安':u'016030',
        u'函館':u'017010',
        u'江差':u'017020',
        u'青森':u'020010',
        u'むつ':u'020020',
        u'八戸':u'020030',
        u'盛岡':u'030010',
        u'宮古':u'030020',
        u'大船渡':u'030030',
        u'仙台':u'040010',
        u'白石':u'040020',
        u'秋田':u'050010',
        u'横手':u'050020',
        u'山形':u'060010',
        u'米沢':u'060020',
        u'酒田':u'060030',
        u'新庄':u'060040',
        u'福島':u'070010',
        u'小名浜':u'070020',
        u'若松':u'070030',
        u'水戸':u'080010',
        u'土浦':u'080020',
        u'宇都宮':u'090010',
        u'大田原':u'090020',
        u'前橋':u'100010',
        u'みなかみ':u'100020',
        u'さいたま':u'110010',
        u'熊谷':u'110020',
        u'秩父':u'110030',
        u'千葉':u'120010',
        u'銚子':u'120020',
        u'館山':u'120030',
        u'東京':u'130010',
        u'大島':u'130020',
        u'八丈島':u'130030',
        u'父島':u'130040',
        u'横浜':u'140010',
        u'小田原':u'140020',
        u'新潟':u'150010',
        u'長岡':u'150020',
        u'高田':u'150030',
        u'相川':u'150040',
        u'富山':u'160010',
        u'伏木':u'160020',
        u'金沢':u'170010',
        u'輪島':u'170020',
        u'福井':u'180010',
        u'敦賀':u'180020',
        u'甲府':u'190010',
        u'河口湖':u'190020',
        u'長野':u'200010',
        u'松本':u'200020',
        u'飯田':u'200030',
        u'岐阜':u'210010',
        u'高山':u'210020',
        u'静岡':u'220010',
        u'網代':u'220020',
        u'三島':u'220030',
        u'浜松':u'220040',
        u'名古屋':u'230010',
        u'豊橋':u'230020',
        u'津':u'240010',
        u'尾鷲':u'240020',
        u'大津':u'250010',
        u'彦根':u'250020',
        u'京都':u'260010',
        u'舞鶴':u'260020',
        u'大阪':u'270000',
        u'神戸':u'280010',
        u'豊岡':u'280020',
        u'奈良':u'290010',
        u'風屋':u'290020',
        u'和歌山':u'300010',
        u'潮岬':u'300020',
        u'鳥取':u'310010',
        u'米子':u'310020',
        u'松江':u'320010',
        u'浜田':u'320020',
        u'西郷':u'320030',
        u'岡山':u'330010',
        u'津山':u'330020',
        u'広島':u'340010',
        u'庄原':u'340020',
        u'下関':u'350010',
        u'山口':u'350020',
        u'柳井':u'350030',
        u'萩':u'350040',
        u'徳島':u'360010',
        u'日和佐':u'360020',
        u'高松':u'370000',
        u'松山':u'380010',
        u'新居浜':u'380020',
        u'宇和島':u'380030',
        u'高知':u'390010',
        u'室戸岬':u'390020',
        u'清水':u'390030',
        u'福岡':u'400010',
        u'八幡':u'400020',
        u'飯塚':u'400030',
        u'久留米':u'400040',
        u'佐賀':u'410010',
        u'伊万里':u'410020',
        u'長崎':u'420010',
        u'佐世保':u'420020',
        u'厳原':u'420030',
        u'福江':u'420040',
        u'熊本':u'430010',
        u'阿蘇乙姫':u'430020',
        u'牛深':u'430030',
        u'人吉':u'430040',
        u'大分':u'440010',
        u'中津':u'440020',
        u'日田':u'440030',
        u'佐伯':u'440040',
        u'宮崎':u'450010',
        u'延岡':u'450020',
        u'都城':u'450030',
        u'高千穂':u'450040',
        u'鹿児島':u'460010',
        u'鹿屋':u'460020',
        u'種子島':u'460030',
        u'名瀬':u'460040',
        u'那覇':u'471010',
        u'名護':u'471020',
        u'久米島':u'471030',
        u'南大東':u'472000',
        u'宮古島':u'473000',
        u'石垣島':u'474010',
        u'与那国島':u'474020',
    }

    @classmethod
    def get_city_id(cls, city_name):
        result = None
        if city_name in cls.NAME_ID_MAP:
            result = cls.NAME_ID_MAP[city_name]
        return result
    
    @classmethod
    def get_city_name(cls, city_id):
        result = None
        if city_id in cls.ID_NAME_MAP:
            result = cls.ID_NAME_MAP[city_id]
        return result
    
    @classmethod
    def get_city_id_list(cls):
        result = []
        result = cls.NAME_ID_MAP.values()
        return result
    
    @classmethod
    def get_city_name_list(cls):
        result = []
        result = cls.NAME_ID_MAP.keys()
        return result

if __name__ == "__main__":
    city_name = u'札幌'
    city_id = CityList.get_city_id(city_name)
    print u"%s -> %s" % (city_name, city_id)
    city_id = u'474020'
    city_name = CityList.get_city_name(city_id)
    print u"%s -> %s" % (city_id, city_name)
    for city_name in CityList.get_city_name_list():
        print city_name
    for city_id in CityList.get_city_id_list():
        print city_id
