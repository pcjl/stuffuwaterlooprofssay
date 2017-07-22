from flask import Flask, request, render_template, Response
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import facebook
import hashlib
import textwrap
import os.path
import sys


app = Flask(__name__)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


@app.route('/', methods=['GET'])
def get_quote():
    return render_template('form.html')


@app.route('/', methods=['POST'])
def post_quote():
    # Constants
    PASSWORD_HASHES = [
        '211f49701abb468c9c686b272a60e15a0b3449651d337f86fea275bcebf98a5d'
    ]

    config = {
        'access_token': 'ACCESS_TOKEN',
        'page_id': 'PAGE_ID'
    }

    QUOTE_SIZE = 60
    SOURCE_SIZE = 40

    MAX_CHARS = 30

    BOTTOM_OFFSET = 150
    LINE_SPACING = 30

    BACKGROUND = resource_path('assets/background.jpg')
    FONT = resource_path('assets/Papyrus.ttf')

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
    source_text = '-{}, {}'.format(professor, course)

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
    filename = r'output/{}.jpg'.format(
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    image.save(filename, quality=95)

    return 'Thanks!'

    graph = facebook.GraphAPI(access_token=config['access_token'])
    response = graph.get_object('me/accounts')
    page_access_token = None
    for page in response['data']:
        if page['id'] == config['page_id']:
            page_access_token = page['access_token']
    graph = facebook.GraphAPI(access_token=page_access_token)
    graph.put_photo(image=open(filename, 'rb'))
