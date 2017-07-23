from flask import Flask, request, render_template, Response
from PIL import Image, ImageDraw, ImageFont
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
        os.environ['PASSWORD_HASH']
    ]

    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

    QUOTE_SIZE = 60
    SOURCE_SIZE = 40

    MAX_CHARS = 32

    BOTTOM_OFFSET = 150
    LINE_SPACING = 30

    BACKGROUND = resource_path('assets/background.jpg')
    FONT = resource_path('assets/Papyrus.ttf')
    OUTPUT = 'output.jpg'

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
    image.save(OUTPUT, quality=95)

    # return 'Thanks!'

    graph = facebook.GraphAPI(access_token=ACCESS_TOKEN)
    response = graph.put_photo(image=open(OUTPUT, 'rb'), message=caption)
    return Response(
            'https://facebook.com/{}'.format(response['post_id']),
            200)
