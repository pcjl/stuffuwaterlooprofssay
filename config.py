import os


SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ['SECRET_KEY']

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
PAGE_ID = os.environ['PAGE_ID']

SOURCE_SIZE = 48

BOTTOM_OFFSET = 150
LINE_SPACING = 30

BACKGROUND = 'background.jpg'
FONT = 'font.ttf'
