#!/bin/bash

# Just because admin needs to wait until db is built
sleep 20s
movies_admin/manage.py runserver 0.0.0.0:8000