## Startup
This needs two servers running at a time, these are the commands:
 * First run the ASGI/WSGI server, this server provides the helios main page and login page rendering
    * env LOG_FILE=django.log PYTHONUNBUFFERED=1 PYTHONPATH=$PWD/../py PYTHONOPTIMIZE=1 python3.6 manage.py runserver 0:8002
       * it's really running daphne like this: env PYTHONOPTIMIZE=1 daphne -p 8001 server.asgi:application --bind 0 --port 8001 --verbosity 1
    * alternatively you can run uvicorn directly instead of django's wrapper around daphne
    * env LOG_FILE=uvicorn.log PYTHONUNBUFFERED=1 PYTHONPATH=$PWD/../py PYTHONOPTIMIZE=1 uvicorn server.asgi:application --host 0 --port 8002 --workers 1 --loop uvloop --ws websockets --reload
 * start the nginx asset server like this, it serves the js/css/images to make sure that the websocket/django server isn't serving standard requests
    * cd <helios root> ; nginx -p $PWD -c server/nginx.conf [-s reload]
