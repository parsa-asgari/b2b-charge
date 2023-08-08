#!/bin/sh
gunicorn tabdeal_assignment.wsgi:application --workers=8 --bind 0.0.0.0:8000