# -*- coding: utf-8 -*-

import datetime
import json
import random
import re
import thread
import time
from bitslack import BitSlack
from event_handler import BotHandler
from exam.models import Category, Problem, User, Score

class QuestionHandler(BotHandler):

    def __init__(self, name):
        BotHandler.__init__(self, name, hear_on_respond=False)
        self.quiz_dict = {}
        self.exam_dict = {}
        self.add_dict = {}
        quiz_patterns= [
            'quiz',
            '出題',
        ]
        score_patterns= [
            'score',
        ]
        exam_patterns= [
            'exam',
        ]
        add_problem_patterns= [
            'add_problem',
        ]
        respond_patterns = [
            (quiz_patterns, self._on_quiz),
            (score_patterns, self._on_score),
            (exam_patterns, self._on_exam),
            (add_problem_patterns, self._on_add_problem),
        ]
        self.set_respond_patterns(respond_patterns)

        hear_patterns = [
            ([".*",], self._on_answer),
        ]
        self.set_hear_patterns(hear_patterns)

    def _on_answer(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return False
        answer = args[0][0]
        channel = event['channel']
        if self.quiz_dict[channel]:
            response = []
            user = None
            try:
                user = User.get(User.name == channel)
            except User.DoesNotExist:
                user = User.create(name=channel, reg_date=datetime.datetime.now())
                user.save()
            problem = self.quiz_dict[channel]
            if answer == problem.answer:
                response.append(u'正解です！')
            else:
                response.append(u'不正解です！（正解は%s）' % (problem.answer))
            response.append(problem.commentary)
            
            self.quiz_dict[channel] = None
            return u"\n".join(response)
        return False
        
    def _on_quiz(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return False
        arg = args[0][0]
        channel = event['channel']
        user = None
        try:
            user = User.get(User.name == channel)
        except User.DoesNotExist:
            user = User.create(name=channel, reg_date=datetime.datetime.now())
            user.save()
        problems = Problem.select().order_by(Problem.id.asc())
        problem = random.choice(problems)
        self.quiz_dict[channel] = problem
        response = []
        response.append(u'[%s]' % (problem.category.id))
        response.append(problem.question)
        return u"\n".join(response)

    def _on_score(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return False
        channel = event['channel']
        user = None
        try:
            user = User.get(User.name == channel)
        except User.DoesNotExist:
            User.create(name=channel, reg_date=datetime.datetime.now())

    def _on_exam(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return False
        return u'すみません、まだ実装中です。'

    def _on_add_problem(self, bitslack_obj, event, args):
        if self.is_bot(event):
            return False
        return u'すみません、まだ実装中です。'

    def on_hello(self, bitslack_obj, event):
        BotHandler.on_hello(self, bitslack_obj, event)
        #bitslack_obj.talk(u'起動しました', 'ueda_302', botname=self.name)

if __name__ == "__main__":
    import settings
    botname = u'試験問題bot'
    bslack = BitSlack(settings.SLACK_API_KEY, botname,
            settings.SLACK_ICON_URL,
            debug=False)
    handler = QuestionHandler(botname)
    
    bslack.add_event_handler(handler)
    bslack.start_rtm()
