# World of Recursers

A world map of where Recurse Center alumni live.

## Local Set Up

### Prepare the database

We use [PostgreSQL](https://www.postgresql.org/) as our database.
Follow the [installation instructions](https://www.postgresql.org/download/)
for your platform to set up the database server.

First, choose or [create](https://www.postgresql.org/docs/current/tutorial-createdb.html)
a database:

```sh
$ createdb --owner=$(whoami) recurseworld
```

Depending on your platform,
you may need to run that command
as the operating system user which owns the database server:

```sh
$ sudo -u postgres createdb --owner=$(whoami) recurseworld
```

Then, create the schema:

```sh
$ psql recurseworld < schema.sql
```

Add your database connection URL to the `.env` file:
`DATABASE_URL=postgres:///recurseworld/`

**Note**: the `DATABASE_URL` can be any
[libpq connection string](https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING).
An alternate database URL you might try is
`postgres://localhost/recurseworld`
to connect over TCP/IP to the database named `recurseworld`.

### Python Virtual Environment
You'll first need to install the Python dependencies.
First, set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

```sh
$ python3 -m venv venv
```

or

```sh
$ python3 -m virtualenv --python=python3 venv
```

Then, activate the virtual environment
and install the app's dependencies into it:

```sh
$ . venv/bin/activate
(venv)$ pip install -r requirements.txt
```

To populate the database,
the scripts must be run in this virtual environment (venv).
The virtual environment can be reactivated at any time with the command:

```sh
$ . venv/bin/activate
```

### Create a .env File
The app needs some configuration,
which it takes through environment variables.
For convenience, this project uses a `.env` file
to store these variables.

First, copy the `env.template` file to a new file named `.env`:

```sh
$ cp env.template .env
```

The next few sections will describe
how to set and add to this initial set of variables.

**Note**: The `.env` file should not be placed under version control
and is included in the `.gitignore` file.

There is a script
to get the data the application needs
from the Recurse Center API
and from the [GeoNames](https://www.geonames.org/) API
and store it in the database.

To connect to the RC API,
the script needs a personal access token,
which you can create in the
[Apps page in your RC Settings](https://www.recurse.com/settings/apps).
The personal access token will only be shown once,
so copy it to a safe place
and add it to the `.env` file:
`RC_API_ACCESS_TOKEN=<personal_access_token>`

To connect to the
[GeoNames API](https://www.geonames.org/export/web-services.html),
the script needs a GeoNames username.
[Create a new user account](https://www.geonames.org/login),
and then enable web services on the
[account management page](https://www.geonames.org/manageaccount).
Add your username to the `.env` file:
`GEONAMES_USER=<your_username>`

To show map data from
[Mapbox](https://www.mapbox.com/),
the front end needs a Mapbox
[public access token](https://docs.mapbox.com/help/glossary/access-token/).
[Create a new user account](https://account.mapbox.com/auth/signup/),
and then add the default public token from your account page
to the `.env` file:
`MAPBOX_ACCESS_TOKEN=<public_access_token>`.

Run the script to populate the database
in your [Python Virtual Environment](#python-virtual-environment):

```sh
(venv)$ ./update-data.py
```

It should print out how many people were added.

### Build the front end

The HTML and JavaScript that the Flask app will serve needs to be built.

First, install the dependencies:

```sh
$ npm install
```

Then, make sure you've sourced your `.env` file,
so that the build can bundle in your Mapbox token:

```sh
$ source .env
```

Finally, run the build:

```sh
$ npm run build
```

### Start the Flask App

When running in development mode,
the app does not require authentication.

If you are working on the RC OAuth integration,
you will need to
[create an OAuth app in your RC Settings](https://www.recurse.com/settings/apps).
Then, update the `.env`
to include the generated client ID and the client secret:
`CLIENT_ID=<your_client_id>` and `CLIENT_SECRET=<your_client_secret>`.
Otherwise, those variables can remain set to the placeholder values
(but must still be present and non-empty).

The `CLIENT_CALLBACK` URL variable must include
the port number the Flask instance will be running on,
which defaults to port 5000. Update this URL in your `.env` file
if using a different port.

Start the Flask API
in your [Python Virtual Environment](#python-virtual-environment):
```sh
(venv)$ flask run
```

Now, your local instance of Recurse World
with live data from the RC API
will be available at http://127.0.0.1:5000/ .

## Heroku Set Up

This is app is deployed on Heroku:

```sh
$ heroku apps:create
```

To set up your Heroku app, add both the Python and Node buildpacks:

```sh
$ heroku buildpacks:add heroku/python
$ heroku buildpacks:add heroku/nodejs
```

You will also need to set several environment variables.

Three relate to the Recurse Center OAuth API. When you create your OAuth app in
your RC account settings, you will need to set the callback to be
`https://<your_url>/auth/recurse/callback`. Once you create it, you will get a
`CLIENT_ID` and `CLIENT_SECRET`. You will also need to set a randomly chosen
password for Flask to encrypt sessions with.

```sh
$ heroku config:set \
    CLIENT_CALLBACK=https://<your_url>/auth/recurse/callback \
    CLIENT_ID=<your_client_id> \
    CLIENT_SECRET=<your_client_secret> \
    FLASK_SECRET_KEY=$(makepasswd --chars=64) \
    FLASK_ENV=production
    GEONAMES_USER=<your_geonames_username> \
    RC_API_ACCESS_TOKEN=<your_rc_api_token> \
    MAPBOX_ACCESS_TOKEN=<your_mapbox_token>
```

You will also need to create a database:

```sh
$ heroku addons:create heroku-postgresql:hobby-dev
```

and populate it:

```sh
$ heroku pg:psql < schema.sql
```

And you'll probably want logs of some sort. I'm using Papertrail:

```sh
$ heroku addons:create papertrail:choklad
```

Then, in theory, it should be a simple `git push heroku master`!

![Licensed under the AGPL, version 3](https://img.shields.io/badge/license-AGPL3-blue.svg)
