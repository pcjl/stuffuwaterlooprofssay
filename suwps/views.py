from urllib.parse import urlparse, urlunparse

import passlib.hash
from flask import (
    redirect,
    request,
    render_template,
    Response,
    url_for
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from suwps import app, db, utils
from suwps.models import User


@app.before_request
def redirect_custom_url():
    url_parts = urlparse(request.url)
    if 'herokuapp' in url_parts.netloc and app.config['CUSTOM_URL']:
        url_parts_list = list(url_parts)
        url_parts_list[1] = app.config['CUSTOM_URL']
        return redirect(urlunparse(url_parts_list), code=301)


@app.route('/', methods=['GET'])
@login_required
def get_index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@login_required
def post_index():
    quote = request.form.get('quote', '').strip()
    professor = request.form.get('prof', '').strip()
    is_professor = 'isprof' in request.form
    course = request.form.get('course', '').strip()
    caption = request.form.get('caption', '').strip()
    date_time = request.form.get('datetime', '')

    if not quote or not professor or not course:
        return Response(
            'Required fields were not filled out.',
            400)

    scheduled_publish_time = utils.convert_time(date_time) \
        if date_time else None

    image = utils.generate_image(
        quote=quote,
        professor=professor,
        is_professor=is_professor,
        course=course)

    response = utils.publish_image(
        image=image,
        professor=professor,
        course=course,
        caption=caption,
        scheduled_publish_time=scheduled_publish_time)

    return Response(
            response.text,
            200)


@app.route('/login', methods=['GET'])
def get_login():
    if current_user.is_authenticated:
        return redirect(url_for('get_index'))

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def post_login():
    username = request.form.get('username', '').lower()
    password = request.form.get('password', '')
    rememberme = 'rememberme' in request.form

    if not username or not password:
        return Response(
            'No username or password supplied.',
            400)

    user = User.query.filter_by(username=username).first()

    if user is not None and user.verify_password(password):
        login_user(user, remember=rememberme)
        return Response(
            'Login successful.',
            200)

    return Response(
            'Invalid credentials supplied.',
            401)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_login'))


@app.route('/register', methods=['GET'])
def get_register():
    if current_user.is_authenticated or not app.config['ENABLE_REGISTRATION']:
        return redirect(url_for('get_index'))
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def post_register():
    if not app.config['ENABLE_REGISTRATION']:
        return Response(
            'Registration is currently disabled.',
            200)

    username = request.form.get('username', '').lower()
    password = request.form.get('password', '')

    if not username or not password:
        return Response(
            'No username or password supplied.',
            400)

    user = User(
        username=username,
        password=passlib.hash.pbkdf2_sha256.hash(password))
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('get_index'))
