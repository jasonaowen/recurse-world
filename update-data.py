#!/usr/bin/env python

'''
Fetch and insert Recurse Center API data into database.

This script fetches the list of profiles from the Recurse Center API using the
personal access token specified in the environment variable
RC_API_ACCESS_TOKEN.

It connects to the database specified in the environment variable DATABASE_URL,
opens a transaction and adds or updates the new data. The database schema must
already exist.
'''

import argparse
import json
import logging
import psycopg2
from psycopg2.extras import Json
import requests
import sys


def getEnvVar(var_name):
    value = os.getenv(var_name)
    if not value:
        logging.error(
            f'"{var_name}" value not found.'
            ' Ensure a .env file is present'
            ' with this environment variable set.'
        )
        sys.exit()

    return value


def get_profiles(token):
    headers = {'Authorization': f'Bearer {token}'}
    limit = 50
    offset = 0

    while True:
        r = requests.get(
            'https://www.recurse.com/api/v1/profiles',
            {
                'limit': limit,
                'offset': offset,
            },
            headers=headers,
        )
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        page = r.json()
        if page == []:
            break
        for profile in page:
            yield profile
        offset += limit


def load_profile(cursor, geoname_user, profile):
    location_name = profile.get('current_location', {}).get('name')
    logging.debug("Profile #{}: {} at {}".format(
        profile.get('id'),
        profile.get('name'),
        location_name,
    ))

    if (location_name is not None and
            not location_is_known(cursor, location_name)):
        location = lookup_location(geoname_user, location_name)
        cursor.execute(
            'INSERT INTO locations'
            ' (name, longitude, latitude, geoname_result)'
            ' VALUES (%s, %s, %s, %s)',
            [
                location_name,
                location['geonames'][0]['lng'],
                location['geonames'][0]['lat'],
                Json(location),
            ]
        )

    cursor.execute(
        'INSERT INTO profiles'
        ' (profile_id, name, image_url, directory_url, location)'
        ' VALUES (%s, %s, %s, %s, %s)'
        ' ON CONFLICT (profile_id)'
        ' DO UPDATE SET'
        '   name = EXCLUDED.name,'
        '   image_url = EXCLUDED.image_url,'
        '   directory_url = EXCLUDED.directory_url,'
        '   location = EXCLUDED.location',
        [
            profile.get('id'),
            profile.get('name'),
            profile.get('image_path'),
            'https://www.recurse.com/directory/' + profile.get('slug'),
            location_name,
        ],
    )


def location_is_known(cursor, location_name):
    cursor.execute('SELECT 1 FROM locations WHERE name = %s', [location_name])
    return cursor.rowcount > 0


def lookup_location(geonames_user, name):
    '''
    Query the GeoNames search API[1] for the given name,
    restricted to state/country and city feature classes[2].
    Returns the entire API result.

    [1] https://www.geonames.org/export/geonames-search.html
    [2] https://www.geonames.org/export/codes.html
    '''

    query = {
        'featureClass': ['A', 'P'],
        'maxRows': 1,
        'q': name,
        'username': geonames_user,
    }
    request = requests.get('https://secure.geonames.org/searchJSON', query)
    return request.json()


def main(database_url, geonames_user, token):
    logging.info('Loading data from Recurse Center API and GeoNames API...')
    connection = psycopg2.connect(database_url)
    cursor = connection.cursor()

    profile_count = 0
    for profile in get_profiles(token):
        profile_count += 1
        load_profile(cursor, geonames_user, profile)

    connection.commit()
    cursor.close()
    connection.close()
    logging.info(f'Loaded {profile_count} profiles and their locations.')


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    database_url = getEnvVar('DATABASE_URL')
    geonames_user = getEnvVar('GEONAMES_USER')
    token = getEnvVar('RC_API_ACCESS_TOKEN')

    main(database_url, geonames_user, token)
