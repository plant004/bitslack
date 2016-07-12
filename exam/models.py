# -*- coding: utf-8 -*-
from peewee import *
from datetime import datetime
import exam_settings as settings

database = SqliteDatabase(settings.DATABASE)

class BaseModel(Model):
    class Meta:
        database = database

class Category(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    reg_date = DateTimeField()

class Problem(BaseModel):
    id = PrimaryKeyField()
    category = ForeignKeyField(Category, related_name='problems')
    question = TextField() 
    answer = TextField() 
    commentary = TextField()
    reg_date = DateTimeField()

class User(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    reg_date = DateTimeField()

class Score(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='scores')
    problem = ForeignKeyField(Problem, related_name='scores')
    answer_count = IntegerField()
    correct_count = IntegerField()
    reg_date = DateTimeField()
    upd_date = DateTimeField()

    class Meta:
        indexes = (
            (('user', 'problem'), True),
        )
def create_tables():
    database.create_tables([
        Category,
        Problem,
        User,
        Score,
    ])
if __name__ == "__main__":
    create_tables()    
