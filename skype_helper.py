# coding: utf-8

import sys
import Skype4Py

import settings

class SkypeHelper(object):
    def __init__(self):
        self.skype = Skype4Py.Skype()
        self.skype.OnMessageStatus = self.on_message
        # 自動ログインとかできない限り多分意味はない
        if self.skype.Client.IsRunning == False:
            skype.client.Start()
        self.skype.Attach()

    def get_chat_by_name(self, name):
        for ct in self.skype.Chats:
            if ct.Name == name:
                return ct

    def send_message(self, message, chat):
        chat.SendMessage(message)

    def on_message(self, message, status):
        if status == 'SENT':
            self.on_message_sent(message)
        elif status == 'RECEIVED':
            self.on_message_received(message)

    def on_message_sent(self, message): 
        pass

    def on_message_received(self, message): 
        # self.send_message(u'hello!', message.Chat)
        pass

if __name__ == '__main__':
    sh = SkypeHelper()
    if len(sys.argv) > 1:
        text = unicode(sys.argv[1], 'utf-8', 'ignore')
        sh.send_message(text) 
    while True: 
        input('')
