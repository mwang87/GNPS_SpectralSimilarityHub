#!/bin/bash

source activate ms2deepscore

celery -A tasks worker -l info -c 1 -Q ms2deepscore --max-tasks-per-child 10 --loglevel INFO

