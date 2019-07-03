"""
Recurse World back-end
"""

from functools import wraps
import logging
import os
from flask import (
    Flask, jsonify, redirect, request, send_from_directory, session, url_for
)
from authlib.flask.client import OAuth
from werkzeug.exceptions import HTTPException
import psycopg2
import sys
from dotenv import load_dotenv
import geojson


load_dotenv()


def getEnvVar(var_name, fallback=""):
    value = os.getenv(var_name) or fallback
    if not value:
        logging.error(
            f'"{var_name}" value not found.'
            ' Ensure a .env file is present'
            ' with this environment variable set.'
        )
        sys.exit()

    logging.info(var_name + ": " + value)
    return value


# pylint: disable=invalid-name
app = Flask(__name__)
app.secret_key = getEnvVar('FLASK_SECRET_KEY', 'development')

logging.basicConfig(level=logging.INFO)

rc = OAuth(app).register(
    'Recurse Center',
    api_base_url='https://www.recurse.com/api/v1/',
    authorize_url='https://www.recurse.com/oauth/authorize',
    access_token_url='https://www.recurse.com/oauth/token',
    client_id=getEnvVar('CLIENT_ID'),
    client_secret=getEnvVar('CLIENT_SECRET'),
)

connection = psycopg2.connect(getEnvVar('DATABASE_URL'))


@app.route('/')
def index():
    "Get the single-page app HTML"
    return send_from_directory('build', 'index.html')


@app.route('/<path:path>')
def static_file(path):
    "Get the single-page app assets"
    return send_from_directory('build', path)


@app.route('/auth/recurse')
def auth_recurse_redirect():
    "Redirect to the Recurse Center OAuth2 endpoint"
    callback = getEnvVar('CLIENT_CALLBACK')
    return rc.authorize_redirect(callback)


@app.route('/auth/recurse/callback', methods=['GET', 'POST'])
def auth_recurse_callback():
    "Process the results of a successful OAuth2 authentication"

    try:
        token = rc.authorize_access_token()
    except HTTPException as e:
        logging.error(
            'Error %s parsing OAuth2 response: %s',
            request.args.get('error', '(no error code)'),
            request.args.get('error_description', '(no error description'),
        )
        return (jsonify({
            'message': 'Access Denied',
            'error': request.args.get('error', '(no error code)'),
            'error_description': request.args.get('error_description',
                '(no error description)'),
        }), 403)

    me = rc.get('profiles/me', token=token).json()
    logging.info("Logged in: %s", me.get('name', ''))

    session['recurse_user_id'] = me['id']
    return redirect(url_for('index'))


def needs_authorization(route):
    """ Use the @needs_authorization annotation to check that a valid session
    exists for the current user."""
    @wraps(route)
    def wrapped_route(*args, **kwargs):
        """Check the session, or return access denied."""
        if app.debug:
            return route(*args, **kwargs)
        elif 'recurse_user_id' in session:
            return route(*args, **kwargs)
        else:
            return (jsonify({
                'message': 'Access Denied',
            }), 403)

    return wrapped_route


@app.route('/api/geo.json')
@needs_authorization
def get_locations():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.name AS name,
               p.image_url,
               p.directory_url,
               l.name AS location_name,
               l.longitude,
               l.latitude
        FROM profiles AS p
          INNER JOIN locations AS l
            on p.location = l.name
        ORDER BY p.profile_id ASC
    """)

    people = cursor.fetchall()
    cursor.close()

    return jsonify(
        geojson.FeatureCollection([
            geojson.Feature(
                geometry=geojson.Point((float(person[4]), float(person[5]))),
                properties={
                    'name': person[0],
                    'image_url': person[1],
                    'directory_url': person[2],
                    'location_name': person[3]
                },
            )
            for person in people
        ])
    )
