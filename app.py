import datetime
import io
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont
import flask
import flask_login
import flask_sslify
import flask_sqlalchemy
import passlib.hash
import pytz
import requests

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')
db = flask_sqlalchemy.SQLAlchemy(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

if 'DYNO' in os.environ:
    sslify = flask_sslify.SSLify(app)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(flask.url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('index'))

        return flask.render_template('login.html')

    username = flask.request.form['username'].lower()
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

    max_chars = 32
    paragraph = textwrap.wrap(quote, width=max_chars)

    extra_lines = (max(0, len(paragraph) - 6) + 1) // 2
    quote_size = 60 - 6 * extra_lines
    if extra_lines:
        max_chars += 6 * extra_lines
        paragraph = textwrap.wrap(quote, width=max_chars)

    text = '\n'.join(paragraph)
    source_text = '-Prof. {}, {}'.format(professor, course)

    quote_font = ImageFont.truetype(
        font=app.config['FONT'],
        size=quote_size)
    source_font = ImageFont.truetype(
        font=app.config['FONT'],
        size=app.config['SOURCE_SIZE'])

    image = Image.open(app.config['BACKGROUND'])
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

    data = {
        'access_token': app.config['ACCESS_TOKEN'],
        'message': caption,
        'published': not scheduled,
    }

    if scheduled:
        data['scheduled_publish_time'] = timestamp

    response = requests.post(
        'https://graph.facebook.com/{}/photos'.format(app.config['PAGE_ID']),
        data=data,
        files={
            'source': file
        })

    return flask.Response(
            response.text,
            200)
