import datetime
import io
import textwrap

import pytz
import requests
from PIL import Image, ImageDraw, ImageFont

from suwps import app


def convert_time(date_time):
    pattern = '%m/%d/%Y %I:%M %p'
    dt = datetime.datetime.strptime(date_time, pattern)

    timezone = pytz.timezone('US/Eastern')
    aware = timezone.localize(dt)

    if aware - datetime.datetime.now(timezone) <= datetime.timedelta(
            minutes=10):
        return False

    td = (
        aware - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return int(td)


def generate_image(quote, professor, is_professor, course):
    max_chars = 32
    paragraph = textwrap.wrap(quote, width=max_chars)

    extra_lines = (max(0, len(paragraph) - 6) + 1) // 2
    quote_size = 72 - 6 * extra_lines
    if extra_lines:
        max_chars += 6 * extra_lines
        paragraph = textwrap.wrap(quote, width=max_chars)

    text = '\n'.join(paragraph)
    source_text = '-Prof. {}, {}'.format(professor, course) if (
        is_professor) else '-{}, {}'.format(professor, course)

    quote_font = ImageFont.truetype(
        font=app.config['FONT_FILE'],
        size=quote_size)
    source_font = ImageFont.truetype(
        font=app.config['FONT_FILE'],
        size=app.config['SOURCE_SIZE'])

    image = Image.open(app.config['BACKGROUND_IMAGE'])
    draw = ImageDraw.Draw(image)
    text_x, text_y = draw.multiline_textsize(
        text,
        font=quote_font,
        spacing=app.config['LINE_SPACING'])
    width, height = image.size
    quote_height = height - app.config['BOTTOM_OFFSET']
    draw.multiline_text(
        ((width - text_x) / 2, (quote_height - text_y) / 2),
        text,
        fill='black',
        font=quote_font,
        spacing=app.config['LINE_SPACING'],
        align='center')

    text_x, text_y = draw.textsize(
        source_text,
        font=source_font)
    draw.text(
        ((width - text_x) / 2, quote_height),
        source_text,
        font=source_font,
        fill='black')

    file = io.BytesIO()
    image.save(file, format="JPEG", quality=95)
    file.seek(0)

    return file


def publish_image(
        image, professor, course, caption, scheduled_publish_time):
    data = {
        'access_token': app.config['ACCESS_TOKEN'],
        'caption': professor + ', ' + course + '\n' + caption,
        'published': not scheduled_publish_time,
    }

    if scheduled_publish_time:
        data['scheduled_publish_time'] = scheduled_publish_time

    response = requests.post(
        'https://graph.facebook.com/{}/photos'.format(app.config['PAGE_ID']),
        data=data,
        files={
            'source': image
        })

    return response
