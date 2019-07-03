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

Run the script to populate the database
in your [Python Virtual Environment](#python-virtual-environment):

```sh
(venv)$ ./update-data.py
```

It should print out how many people were added.


![Licensed under the AGPL, version 3](https://img.shields.io/badge/license-AGPL3-blue.svg)
