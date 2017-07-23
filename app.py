from flask import Flask, request, render_template, Response
from PIL import Image, ImageDraw, ImageFont
import ast
import datetime
import hashlib
import os.path
import pytz
import requests
import sys
import textwrap


app = Flask(__name__)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Constants
PASSWORD_HASHES = [
    os.environ['PASSWORD_HASH_PATRICK'],
    os.environ['PASSWORD_HASH_JESSICA']
]
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
PAGE_ID = os.environ['PAGE_ID']

QUOTE_SIZE = 60
SOURCE_SIZE = 40

MAX_CHARS = 32

BOTTOM_OFFSET = 150
LINE_SPACING = 30

BACKGROUND = resource_path('assets/background.jpg')
FONT = resource_path('assets/Papyrus.ttf')
OUTPUT = 'output.jpg'


@app.route('/', methods=['GET'])
def get_quote():
    return render_template('form.html')


@app.route('/', methods=['POST'])
def post_quote():
    password_hash = hashlib.sha256(
            str(request.form.get('password')).encode('utf-8')).hexdigest()
    if password_hash not in PASSWORD_HASHES:
        return Response(
            'Invalid credentials',
            401,
            {'WWWAuthenticate': 'Basic realm="Login Required"'})

    # Input
    quote = request.form.get('quote')
    professor = request.form.get('prof')
    course = request.form.get('course')
    caption = request.form.get('caption')

    date_time = request.form.get('datetime')
    scheduled = date_time != ''

    if scheduled:
        pattern = '%m/%d/%Y %I:%M %p'
        dt = datetime.datetime.strptime(date_time, pattern)

        timezone = pytz.timezone('US/Eastern')
        aware = timezone.localize(dt)
        td = (
            aware - datetime.datetime(
                1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
        timestamp = int(td)

    # Load resources
    image = Image.open(BACKGROUND)
    quote_font = ImageFont.truetype(
        font=FONT,
        size=QUOTE_SIZE)
    source_font = ImageFont.truetype(
        font=FONT,
        size=SOURCE_SIZE)

    # Parse data
    width, height = image.size
    quote_height = height - BOTTOM_OFFSET

    paragraph = textwrap.wrap(quote, width=MAX_CHARS)
    text = '\n'.join(paragraph)
    source_text = '-Prof. {}, {}'.format(professor, course)

    # Draw quote text
    draw = ImageDraw.Draw(image)
    text_x, text_y = draw.multiline_textsize(
        text,
        font=quote_font,
        spacing=LINE_SPACING)
    draw.multiline_text(
        ((width - text_x) / 2, (quote_height - text_y) / 2),
        text,
        fill='black',
        font=quote_font,
        spacing=LINE_SPACING,
        align='center')

    # Draw source text
    text_x, text_y = draw.textsize(
        source_text,
        font=source_font)
    draw.text(
        ((width - text_x) / 2, quote_height),
        source_text,
        font=source_font,
        fill='black')

    # Save file
    image.save(OUTPUT, quality=95)

    data = {
        'access_token': ACCESS_TOKEN,
        'message': caption,
        'published': not scheduled,
    }

    if scheduled:
        data['scheduled_publish_time'] = timestamp

    response = requests.post(
        'https://graph.facebook.com/{}/photos'.format(PAGE_ID),
        data=data,
        files={
            'source': open(OUTPUT, 'rb')
        })

    scheduled_posts_url = (
        'https://facebook.com/{}/publishing_tools'
        '/?section=SCHEDULED_POSTS'
    ).format(PAGE_ID)

    return Response(
            'https://facebook.com/{}'.format(
                ast.literal_eval(response.text)[
                    'post_id']) if not scheduled else scheduled_posts_url,
            200)
