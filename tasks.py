from celery import Celery
import glob
import sys

celery_instance = Celery('tasks', backend='redis://gnpssimilarity-redis', broker='pyamqp://guest@gnpssimilarity-rabbitmq//', )

@celery_instance.task(time_limit=60)
def task_computeheartbeat():
    print("UP", file=sys.stderr, flush=True)
    return "Up"


@celery_instance.task(time_limit=60)
def tasks_compute_similarity_usi(usi1, usi2):
    
    return "Done"


# celery_instance.conf.beat_schedule = {
#     "cleanup": {
#         "task": "tasks._task_cleanup",
#         "schedule": 3600
#     }
# }


celery_instance.conf.task_routes = {
    'tasks.task_computeheartbeat': {'queue': 'worker'},
}