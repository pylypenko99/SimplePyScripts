#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# SOURCE: https://github.com/coleifer/peewee/blob/afdf7b752dcadbf440faaa91a7fb0f403eac9a69/examples/diary.py


from collections import OrderedDict
import datetime as DT
import hashlib
from getpass import getpass

# pip install peewee
from peewee import *

from utils.security import CryptoAES, AuthenticationError
from utils.utils import shorten


db = SqliteDatabase('my_database.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


# Password: 123
ENCRYPT_KEY = 'A665A45920422F9D417E4867EFDC4FB8A04A1F3FFF1FA07E998E86F7F7A27AE3'
# OR:
# ENCRYPT_KEY = None

if not ENCRYPT_KEY:
    #
    # OR ENCRYPT_KEY using password:
    #
    # Need password
    password = getpass()
    if not password:
        print('Required password!')
        quit()

    ENCRYPT_KEY = hashlib.sha256(bytes(password, 'utf-8')).hexdigest().upper()


class Diary(BaseModel):
    encrypt_content = TextField()
    created_date = DateTimeField(default=DT.datetime.now)

    @staticmethod
    def create_encrypt_content(content: str, key: str) -> 'Diary':
        encrypt_content = CryptoAES(key).encrypt(content)
        return Diary(encrypt_content=encrypt_content).save()

    def get_content(self, key: str) -> str:
        try:
            return CryptoAES(key).decrypt(self.encrypt_content)
        except AuthenticationError as e:
            return f'ERROR: {e}'

    @staticmethod
    def print_table(key: str = ENCRYPT_KEY):
        """Print all diaries"""

        header_fmt = '{:<3}  | {:<50} | {:<50} | {:<19}'
        row_fmt = '#{id:<3} | {encrypt_content:<50} | {content:<50} | {created_date:%d/%m/%Y %H:%M:%S}'

        print(header_fmt.format('ID', 'ENCRYPT_CONTENT', 'CONTENT', 'CREATED_DATE'))

        for diary in Diary.select():
            print(row_fmt.format(
                id=diary.id,
                encrypt_content=shorten(diary.encrypt_content),
                content=shorten(diary.get_content(key)),
                created_date=diary.created_date,
            ))

        print()

    def __str__(self):
        return f'Diary<' \
               f'#{self.id} ' \
               f'encrypt_content={repr(shorten(self.encrypt_content))} ' \
               f'content={repr(shorten(self.get_content(ENCRYPT_KEY)))} ' \
               f"created_date='{self.created_date:%d/%m/%Y %H:%M:%S}'" \
               f">"


db.connect()
db.create_tables([Diary])


# Вызываем в первый раз, чтобы заполнить таблицу
if not Diary.select().count():
    Diary.create_encrypt_content(content="Hello World!", key=ENCRYPT_KEY)
    Diary.create_encrypt_content(content="The quick brown fox jumps over the lazy dog.", key=ENCRYPT_KEY)


def add_diary(key: str = ENCRYPT_KEY):
    """Add diary"""

    data = input('Enter your diary: ').strip()
    if data and input('Save diary? [Y/n] ') != 'n':
        Diary.create_encrypt_content(content=data, key=key)
        print('Saved successfully.')


def view_diaries(key: str = ENCRYPT_KEY):
    """View previous diaries"""

    query = Diary.select().order_by(Diary.created_date.desc())
    for diary in query:
        print()
        timestamp = diary.created_date.strftime('%d/%m/%Y %H:%M:%S')
        print(timestamp)
        print('=' * len(timestamp))
        print(diary.encrypt_content)
        print(diary.get_content(key))
        print()
        print('n) next diary')
        print('d) delete diary')
        print('q) return to main menu')
        action = input('Choice? (N/d/q) ').lower().strip()
        if action == 'q':
            break
        elif action == 'd':
            diary.delete_instance()
            break


MENU = OrderedDict([
    ('a', add_diary),
    ('v', view_diaries),
    ('p', Diary.print_table),
])


def menu_loop():
    choice = None
    while choice != 'q':
        for key, value in MENU.items():
            print('%s) %s' % (key, value.__doc__))
        choice = input('Action: ').lower().strip()
        if choice in MENU:
            MENU[choice]()


Diary.print_table(ENCRYPT_KEY)

menu_loop()
