#!/bin/sh
 export C_FORCE_ROOT=true
# nohup celery worker -l info -A sales_platform --beat  &
celery worker -l info -A sales_platform --beat
