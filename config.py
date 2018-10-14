import os


__DIR__ = os.path.dirname(__file__)

DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

CUSTOM_URL = os.environ.get('CUSTOM_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
PAGE_ID = os.environ.get('PAGE_ID', '')

BACKGROUND_IMAGE = os.path.join(__DIR__, 'suwps', 'assets', 'background.jpg')
FONT_FILE = os.path.join(__DIR__, 'suwps', 'assets', 'font.ttf')
SOURCE_SIZE = 48
BOTTOM_OFFSET = 150
LINE_SPACING = 30

ENABLE_REGISTRATION = False
