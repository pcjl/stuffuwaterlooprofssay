from flask_sslify import SSLify
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import flask
import flask_login
import hashlib
import os
import pytz
import requests
import textwrap

app = flask.Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

if 'DYNO' in os.environ:
    sslify = SSLify(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {
    'patrick': {
        'password': os.environ['PASSWORD_HASH_PATRICK']
    },
    'jessica': {
        'password': os.environ['PASSWORD_HASH_JESSICA']
    }
}

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
PAGE_ID = os.environ['PAGE_ID']

QUOTE_SIZE = 60
SOURCE_SIZE = 40

MAX_CHARS = 32

BOTTOM_OFFSET = 150
LINE_SPACING = 30

BACKGROUND = 'background.jpg'
FONT = 'Papyrus.ttf'


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def load_user(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def load_request(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    password_hash = hashlib.sha256(
        str(flask.request.form.get('password')).encode('utf-8')).hexdigest()
    user.is_authenticated = password_hash == users[username]['password']

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(flask.url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('index'))

        return flask.render_template('login.html')

    username = flask.request.form['username']
    password_hash = hashlib.sha256(
        str(flask.request.form.get('password')).encode('utf-8')).hexdigest()

    if password_hash == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(
            user,
            remember=bool(flask.request.form.getlist('rememberme')))
        return flask.Response(
            'Login successful',
            200)

    return flask.Response(
            'Invalid credentials',
            401)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')

    # Input
    quote = flask.request.form.get('quote')
    professor = flask.request.form.get('prof')
    course = flask.request.form.get('course')
    caption = flask.request.form.get('caption')

    date_time = flask.request.form.get('datetime')
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
    file = BytesIO()
    image.save(file, format="JPEG", quality=95)
    file.seek(0)

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
            'source': file
        })

    return flask.Response(
            response.text,
            200)
