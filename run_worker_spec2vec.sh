#!/bin/bash

source activate spec2vec

celery -A tasks worker -l info -c 1 -Q spec2vec --max-tasks-per-child 10 --loglevel INFO

