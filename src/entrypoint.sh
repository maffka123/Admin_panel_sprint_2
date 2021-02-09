#!/bin/bash

# Just because admin needs to wait until db is built
sleep 30s
cd movies_admin
gunicorn --bind 0.0.0.0:8000 config.wsgi