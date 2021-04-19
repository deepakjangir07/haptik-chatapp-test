web: gunicorn chat.wsgi --log-file -

web: daphne chat.asgi:application --port $PORT --bind 0.0.0.0 -v2

