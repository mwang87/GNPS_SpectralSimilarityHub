#!/bin/bash

source activate simile

celery -A tasks worker -l info -c 1 -Q simile --max-tasks-per-child 10 --loglevel INFO

