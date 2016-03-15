# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import datetime
import re
import thread
import time
from bitslack import BitSlack
from event_handler import BotHandler
from pickle_utils import load, save
from selenium_utils import SeleniumUtils
from simple_aes import SimpleAES
import settings

class AipoUtils(SeleniumUtils):
    def login(self, login_path=None, username_selector=None, username=None, password_selector=None, password=None, login_btn_selector=None):
        try:
            lp = self.login_path
            if login_path is not None:
                lp = login_path
            us = self.username_selector
            if username_selector is not None:
                us = username_selector
            u = self.username
            if username is not None:
                u = username
            ps = self.password_selector
            if password_selector is not None:
                ps = password_selector
            p = self.password
            if password is not None:
                p = password
            lbs = self.login_btn_selector
            if login_btn_selector is not None:
                lbs = login_btn_selector

            self.get_page(lp)
            self.click('#usr_list')
            self.clear(us)
            self.send_keys(u, us)
            self.clear(ps)
            self.send_keys(p, ps)
            self.click(lbs)
            self.login_flg = True
        except Exception, e:
            self.quit()
            raise e

class TimeFormatter(object):

    Q = 5

    def quantize(self, start_datetime, end_datetime, q):
        result = (start_datetime, end_datetime)
        q_float = float(TimeFormatter.Q)
        try:
            start_h = start_datetime.hour
            start_m = start_datetime.minute
            # qにあわせる
            start_m = int(math.floor(start_m / q_float) * q)

            end_h = end_datetime.hour
            end_m = end_datetime.minute
            # qにあわせる
            end_m = int((round(end_m / q_float, 0)) * q)
            # 開始・終了が同じ時間の場合は1単位分終了をずらす
            if end_m == start_m and end_h == start_h:
                if end_h != 24 and end_m != 0:
                    end_m += q
                else:
                    # 終了時刻が夜の場合は
                    start_h = 23
                    start_m = 55
            # 60を超えていた場合の調整
            if end_m >= 60:
                end_h += 1
                end_m = end_m % 60
            shd = start_h - start_datetime.hour
            smd = start_m - start_datetime.minute
            ehd = end_h - end_datetime.hour
            emd = end_m - end_datetime.minute
            q_start_datetime = start_datetime + datetime.timedelta(hours=shd, minutes=smd)
            q_end_datetime = end_datetime + datetime.timedelta(hours=ehd, minutes=emd)
            result = (q_start_datetime, q_enddatetime)
        except Exception, e:
            print e
            pass
        return result
        
class AipoHandler(BotHandler):
    """ Aipoの出退勤および会議室の予約を行うためのHandler """
    FILE_PATH = 'aipo_authinfo.txt'
    ATTEND_PATTERNS = [
        u'出勤',
        u'attend',
    ]
    LEAVE_PATTERNS = [
        u'退勤',
        u'leave',
    ]
    RESERVE_PATTERNS = [
        u'予約',
        u'reserve',
    ]
    AUTHINFO_PATTERNS = [
        u'認証情報',
        u'authinfo',
    ]
    PATTERN_TYPE_HH = 1
    PATTERN_TYPE_MM = 2
    PATTERN_TYPE_AFTER = 4
    PATTERN_TYPE_HHMM = PATTERN_TYPE_HH|PATTERN_TYPE_MM
    PATTERN_TYPE_HH_AFTER = PATTERN_TYPE_HH|PATTERN_TYPE_AFTER
    PATTERN_TYPE_MM_AFTER = PATTERN_TYPE_MM|PATTERN_TYPE_AFTER
    PATTERN_TYPE_HHMM_AFTER = PATTERN_TYPE_HHMM|PATTERN_TYPE_AFTER

    def __init__(self, name=None):
        """ 各コマンドのパターンと認証情報の初期化 """
        BotHandler.__init__(self, name)
        respond_patterns = [
            (self.ATTEND_PATTERNS, self.handle_attend),
            (self.LEAVE_PATTERNS, self.handle_leave),
            (self.RESERVE_PATTERNS, self.handle_reserve),
            (self.AUTHINFO_PATTERNS, self.handle_authinfo),
        ]
        self.set_respond_patterns(respond_patterns)
        self.command_status = {}
        self._init_attend()
        self._init_leave()
        self._init_reserve()
        self._init_authinfo()


    def _init_attend(self):
        """ 出勤コマンドの初期化 """
        description = u'Aipoの出勤ボタンを押します。'.encode('utf-8')
        prog = (u'@slackbot %s' % (u'|'.join(self.ATTEND_PATTERNS))).encode('utf-8')
        parser = ArgumentParser(description=description, prog=prog, add_help=False)
        parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))
        self.attend_parser = parser

    def _init_leave(self):
        """ 退勤コマンドの初期化 """
        description = u'Aipoの退勤ボタンを押します。'.encode('utf-8')
        prog = (u'@slackbot %s' % (u'|'.join(self.LEAVE_PATTERNS))).encode('utf-8')
        parser = ArgumentParser(description=description, prog=prog, add_help=False)
        parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))
        self.leave_parser = parser

    def _init_reserve(self):
        """ 予約コマンドの初期化 """
        pass
        description = u'Aipoの出勤ボタンを押します。'.encode('utf-8')
        prog = (u'@slackbot %s' % (u'|'.join(self.RESERVE_PATTERNS))).encode('utf-8')
        parser = ArgumentParser(description=description, prog=prog, add_help=False)
        parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))
        parser.add_argument('-t', '--title', dest='title', default='', help=u'予定のタイトルを指定'.encode('utf-8'))
        parser.add_argument('-m', '--members', dest='members', default='', help=u'メンバーを指定'.encode('utf-8'))
        parser.add_argument('-r', '--room', dest='room', default='', help=u'予約する部屋を指定'.encode('utf-8'))
        parser.add_argument('-s', '--start-time', dest='start_time', default='', help=u'HH:mm, HH時mm分で使用開始時刻を指定'.encode('utf-8'))
        parser.add_argument('-e', '--end-time', dest='end_time', default='', help=u'HH:mm, HH時mm分, HH時間後, mm分後などで使用終了時刻を指定'.encode('utf-8'))
        self.reserve_parser = parser

    def _init_authinfo(self):
        """ 認証情報設定コマンドの初期化 """
        description = u'Aipoの認証情報を設定します。'.encode('utf-8')
        prog = (u'@slackbot %s' % (u'|'.join(self.AUTHINFO_PATTERNS))).encode('utf-8')
        parser = ArgumentParser(description=description, prog=prog, add_help=False)
        parser.add_argument('-h', '--help', action='store_true', dest='usage', help=u'ヘルプを表示します。'.encode('utf-8'))
        parser.add_argument('-u', '--username', dest='username', default='', help=u'AipoのユーザーIDを指定'.encode('utf-8'))
        parser.add_argument('-p', '--password', dest='password', default='', help=u'Aipoのパスワードを指定'.encode('utf-8'))
        self.authinfo_parser = parser
        # データ読み込み
        self.enc = SimpleAES(settings.AIPO_KEY)
        self._load_authinfo_list()
        self._save_authinfo_list()

    def _load_authinfo_list(self):
        authinfo_data = load(self.FILE_PATH, None)
        self.authinfo_list = {}
        if authinfo_data is not None:
            for k, v in authinfo_data.items():
                userid, password = v
                self.authinfo_list[k] = (self.enc.decrypt(userid), self.enc.decrypt(password))

    def _save_authinfo_list(self):
        authinfo_data = {}
        for k, authinfo in self.authinfo_list.items():
            userid, password = authinfo
            authinfo_data[k] = (self.enc.encrypt(userid), self.enc.encrypt(password))
        save(authinfo_data, self.FILE_PATH)

    def handle_common(self, bitslack_obj, event, args, parser):
        """ 共通のハンドリング処理(usageの有無、ユーザ情報の存在確認、ログインなど) """
        result = (None, None, None)
        if not self.is_bot(event):
            user_str = self.get_event_user_str(event)
            text_list = event['text'].split()
            cmd_args, unknown_args = parser.parse_known_args(text_list)
            if cmd_args.usage:
                usage = parser.format_help()
                texts = usage.decode('utf-8')
                self.talk(bitslack_obj, texts, event)
            else:
                userid = event['user']
                if userid in self.authinfo_list:
                    username, password = self.authinfo_list[userid]
                    config = {
                        'base_url': settings.AIPO_BASE_URL,
                        'login_path': settings.AIPO_LOGIN_PATH,
                        'username': username,
                        'password': password,
                        'username_selector': 'input[name="member_username"]',
                        'password_selector': 'input[name="password"]',
                        'login_btn_selector': 'input[name="login_submit"]',
                    }
                    au = AipoUtils(config)
                    texts = u'ログイン中です...'
                    self.talk(bitslack_obj, texts, event)
                    au.login()
                    result = (user_str, cmd_args, au)
                else:
                    self.command_status[userid] = cmd_args
                    user = bitslack_obj.get_user_by_id(userid)
                    texts = [u'認証情報を教えて下さい。',]
                    usage = self.authinfo_parser.format_help()
                    texts.append(usage.decode('utf-8'))
                    channel = user['name']
                    bitslack_obj.talk(texts, channel)
        return result

    def handle_attend(self, bitslack_obj, event, args):
        """ 出勤ボタンを押下する """
        return self._handle_click_button(bitslack_obj, event, args, is_attend=True) 

    def handle_leave(self, bitslack_obj, event, args):
        """ 退勤ボタンを押下する """
        return self._handle_click_button(bitslack_obj, event, args, is_attend=False) 
    
    def _handle_click_button(self, bitslack_obj, event, args, is_attend):
        """ ボタンを押下する """
        result = None
        if is_attend:
            parser = self.attend_parser
            selector = 'input[name="punchin"]'
            command_str = u'出勤'
        else:
            parser = self.leave_parser
            selector = 'input[name="punchout"]'
            command_str = u'退勤'
        user_str, cmd_args, au = self.handle_common(bitslack_obj, event, args, parser)
        if au:
            texts = u'ログイン完了しました。続けて%sボタンを押します...' % (command_str)
            self.talk(bitslack_obj, texts, event)
            if au.find(selector):
                au.click(selector)
                # 成否を返す
                if au.find(selector):
                    result = u'%s %sボタンが押せませんでした。既に%sしているか、認証情報が間違っている可能性があります。' % (user_str, command_str, command_str)
                else: 
                    result = u'%s %sしました。' % (user_str, command_str)
            else:
                # ボタンが見つからないことを返す
                result = u'%s %sボタンが見つかりませんでした。既に%sしているか、認証情報が間違っている可能性があります。' % (user_str, command_str, command_str)
            au.logout(settings.AIPO_LOGOUT_PATH)
            au.quit()
        return result

    def handle_reserve(self, bitslack_obj, event, args):
        """ 施設を予約する """
        result = None
        parser = self.reserve_parser
        user_str, cmd_args, au = self.handle_common(bitslack_obj, event, args, parser)
        # 時間の解析
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
        if cmd_args.start_time != '':
            start_time = self._parse_time(cmd_args.start_time)
        if cmd_args.end_time != '':
            end_time = self._parse_time(cmd_args.end_time, start_time)
        start_time_text = start_time.strftime('%H:%M')
        end_time_text = end_time.strftime('%H:%M')
        # 部屋名等のオプションの解析
        #parser.add_argument('-t', '--title', dest='title', default='', help=u'予定のタイトルを指定'.encode('utf-8'))
        #parser.add_argument('-m', '--members', dest='members', default='', help=u'メンバーを指定'.encode('utf-8'))
        #parser.add_argument('-r', '--room', dest='room', default='', help=u'予約する部屋を指定'.encode('utf-8'))
        # カレンダーで予定作成
        link_text = u'カレンダー'
        if au.find(text=link_text):
            au.click(text=link_text)
            add_schedule_btn_selector = u'#予定を追加する_Button1'
            
        #user_str = self.get_event_user_str(event)
        #text_list = event['text'].split()
        #args, unknown_args = self.parser.parse_known_args(text_list)
        #if args.usage:
        #    usage = self.parser.format_help()
        #    return usage.decode('utf-8')

        #text_without_message = re.sub(args.message, '', event['text'])
        #sleep_time, timer_text = self._parse_sleep_time(text_without_message)
        #start_time = datetime.datetime.now()
        #text = u'%s: %sにタイマを設定しました。' % (user_str, timer_text)
        #def timer_thread(*args):
        #    sleep_time = args[0]
        #    user_str = args[1]
        #    message = args[2]
        #    time.sleep(sleep_time)
        #    end_time = datetime.datetime.now()
        #    timer_finished = u'%s: タイマ設定時刻になりました。%s' % (args[1], args[2])
        #    bitslack_obj.talk(timer_finished, event['channel'], botname=self.name)
        #thread.start_new_thread(timer_thread, (sleep_time, user_str, args.message))
        #return text
        return result

    def handle_authinfo(self, bitslack_obj, event, args):
        """ 認証情報の設定 """
        parser = self.authinfo_parser
        result = None
        if not self.is_bot(event):
            user_str = self.get_event_user_str(event)
            text_list = event['text'].split()
            cmd_args, unknown_args = parser.parse_known_args(text_list)
            if cmd_args.usage:
                usage = parser.format_help()
                texts = usage.decode('utf-8')
                self.talk(bitslack_obj, texts, event)
            else:
                channel = event['channel']
                username = cmd_args.username
                password = cmd_args.password
                if username != '' and password != '':
                    userid = event['user']
                    self.authinfo_list[userid] = (username, password)
                    self._save_authinfo_list()
                    texts = u'認証情報を登録しました。'
                else:
                    texts = u'ユーザIDまたはパスワードが空です。'
                bitslack_obj.talk(texts, channel)
        return result

    def _parse_time(self, text, start_time=None):
        """ 時間の記述をdatetime型へ変換する """
        result = None
        text = re.sub(u'タイマー?[ 　]*', '', text)

        hhmm_after_patterns = [
            u'(\d{1,2})時間(\d{1,2})分後',
        ]

        hhmm_patterns = [
            u'(\d{1,2}):(\d{1,2})',
            u'(\d{1,2})時(\d{1,2})分',
        ]

        hh_after_patterns = [
            u'(\d{1,2})時間後',
        ]

        hh_patterns = [
            u'(\d{1,2})時',
        ]

        mm_after_patterns = [
            u'(\d{1,2})分後',
        ]

        mm_patterns = [
            u'(\d{1,2})分',
        ]

        match = None
        if start_time:
            match = self._match_time_patterns(text, hhmm_after_patterns, AipoHandler.PATTERN_TYPE_HHMM_AFTER)
        if match is None:
            match = self._match_time_patterns(text, hhmm_patterns, AipoHandler.PATTERN_TYPE_HHMM)
        if start_time and match is None:
            match = self._match_time_patterns(text, hh_after_patterns, AipoHandler.PATTERN_TYPE_HH_AFTER)
        if match is None:
            match = self._match_time_patterns(text, hh_patterns, AipoHandler.PATTERN_TYPE_HH)
        if start_time and match is None:
            match = self._match_time_patterns(text, mm_after_patterns, AipoHandler.PATTERN_TYPE_MM_AFTER)
        if match is None:
            match = self._match_time_patterns(text, mm_patterns, AipoHandler.PATTERN_TYPE_MM)

        if match is not None:
            match_text = match[0]
            h = int(match[1])
            m = int(match[2])
            after_flg = match[3]
            if start_time:
                now_datetime = start_time
            else:
                now_datetime = datetime.datetime.now()
            s = 0
            days_delta = 0
            if after_flg:
                s = now_datetime.second
                if m < 0:
                    m = now_datetime.minute
                else:
                    m = now_datetime.minute + m
                if h < 0:
                    h = now_datetime.hour
                else:
                    h = now_datetime.hour + h
            else:
                if m < 0:
                    m = 0
                if h < 0:
                    h = now_datetime.hour
            if 59 < m:
                h_delta, new_m = divmod(m, 60)
                h = h + h_delta
                m = new_m
            if 23 < h:
                d_delta, new_h = divmod(h, 24)
                days_delta = d_delta
                h = new_h
            #print '%s:%s' % (h, m)
            result_datetime = datetime.datetime(now_datetime.year, now_datetime.month, now_datetime.day, h, m, s)
            result_datetime = result_datetime + datetime.timedelta(days=days_delta)
            if result_datetime < now_datetime:
                result_datetime = result_datetime + datetime.timedelta(days=1)
            result = result_datetime
        return result

    def _match_time_patterns(self, text, patterns, pattern_types):
        result = None
        match_text = None
        h = -1
        m = -1
        after_flg = False
        for pattern in patterns:
            match = re.search(pattern, text)
            if match is not None:
                match_text = match.group(0)
                if AipoHandler.PATTERN_TYPE_HH & pattern_types:
                    h = match.group(1)
                    if AipoHandler.PATTERN_TYPE_MM & pattern_types:
                        m = match.group(2)
                    
                elif AipoHandler.PATTERN_TYPE_MM & pattern_types:
                    m = match.group(1)
                if AipoHandler.PATTERN_TYPE_AFTER & pattern_types:
                    after_flg = True
                result = (match_text, h, m, after_flg)
                break
        return result


if __name__ == "__main__":
    import settings
    botname = 'aipo bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    bslack.add_event_handler(AipoHandler(botname))
    bslack.start_rtm()
