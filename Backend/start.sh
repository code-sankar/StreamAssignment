#!/bin/bash
echo "Starting Livestream Backend on Render..."
exec gunicorn --config gunicorn.conf.py wsgi:app