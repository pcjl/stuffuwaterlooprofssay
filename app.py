import datetime
import io
import os
import requests
import textwrap

import flask
import flask_login
import flask_sslify
import flask_sqlalchemy
import passlib.hash
import PIL
import pytz

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)

app.secret_key = os.environ['SECRET_KEY']
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

if 'DYNO' in os.environ:
    sslify = flask_sslify.SSLify(app)

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
PAGE_ID = os.environ['PAGE_ID']

QUOTE_SIZE = 60
SOURCE_SIZE = 40

MAX_CHARS = 32

BOTTOM_OFFSET = 150
LINE_SPACING = 30

BACKGROUND = 'background.jpg'
FONT = 'Papyrus.ttf'


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(120))

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return '<username {}>'.format(self.username)


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


@login_manager.request_loader
def load_request(request):
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None:
        return

    user.is_authenticated = passlib.hash.pbkdf2_sha256.verify(
        password, user.password)

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
    password = flask.request.form.get('password')
    rememberme = bool(flask.request.form.getlist('rememberme'))

    user = User.query.filter_by(username=username).first()

    if user is not None and passlib.hash.pbkdf2_sha256.verify(
            password, user.password):
        flask_login.login_user(user, remember=rememberme)
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
    image = PIL.Image.open(BACKGROUND)
    quote_font = PIL.ImageFont.truetype(
        font=FONT,
        size=QUOTE_SIZE)
    source_font = PIL.ImageFont.truetype(
        font=FONT,
        size=SOURCE_SIZE)

    # Parse data
    width, height = image.size
    quote_height = height - BOTTOM_OFFSET

    paragraph = textwrap.wrap(quote, width=MAX_CHARS)
    text = '\n'.join(paragraph)
    source_text = '-Prof. {}, {}'.format(professor, course)

    # Draw quote text
    draw = PIL.ImageDraw.Draw(image)
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
    file = io.BytesIO()
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
