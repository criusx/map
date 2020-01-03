# helios

helios is a comprehensive visualization and analysis toolsuite.

See documents in django/README.md for setting up a server

## Setup under Ubuntu

- sudo apt install libssl-dev libldap2-dev libsasl2-dev python-dev
- sudo pip3 install django-auth-ldap django-cors-headers psycopg2-binary Beaker dask numba colorama==0.4.1 hdf5plugin toolz fsspec cloudpickle python-ldap channels django-channels uvicorn==0.10.0 tables gitpython

## Setup and run servers

- three different servers are required to run helios correctly
  - the ASGI server, which includes django, creates the dynamic web pages and serves data via a websocket interface
  - a backend database, which provides storage for user data and other state
  - a nginx web server, which serves static assets like javascript, images, etc.

- from the helios/django directory, run this to start the django/ASGI server
  - env LOG_FILE=uvicorn.log PYTHONUNBUFFERED=1 PYTHONPATH=$PWD/../py PYTHONOPTIMIZE=1 uvicorn server.asgi:application --host 0 --port 8002 --workers 1 --loop uvloop --ws websockets --reload
  
- this requires a database backend, currently it's setup for PostgresSQL
  - sudo apt install postgresql
  - sudo -u postgres -i
  - create the database user and make an initial database
    - createuser --interactive --pwprompt
      - it's configured for 'helios' and 'heliosPwd' in django/server/settings.py, choose whatever works
    - createdb -O helios helios
    - exit
  - create the schema that the django ORM will use
    - python3 manage.py makemigrations server
    - python3 manage.py migrate
    - python3 manage.py shell
  - then add username(s) for access to the helios tool
    - from server.models import AuthenticatedUser
    - AuthenticatedUser.objects.create(username='<newuser>')
  
- finally, you need nginx to run as a static asset server, you don't want django serving static files and wasting its time
  - sudo apt install nginx
  - nginx -c server/nginx.conf -p $PWD
 
For other general helios documentation, see `docs/`
