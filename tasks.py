from celery import Celery
import glob
import sys
from joblib import Memory

memory = Memory("temp/memory-cache", verbose=0)

try:
    import run_spec2vec
except:
    print("Spec2Vect IMPORT FAILURE")
    pass

try:
    import run_simile
except:
    print("SIMILE IMPORT FAILURE")
    pass

try:
    import run_gnps
except:
    print("GNPS IMPORT FAILURE")
    pass

try:
    import run_ms2deepscore
except:
    print("MS2Deep IMPORT FAILURE")
    pass

try:
    import run_spectralentropy
except:
    print("Spectral Entropy IMPORT FAILURE")
    pass

celery_instance = Celery('tasks', backend='redis://gnpssimilarity-redis', broker='pyamqp://guest@gnpssimilarity-rabbitmq//', )

@celery_instance.task(time_limit=60)
def task_computeheartbeat():
    print("UP", file=sys.stderr, flush=True)
    return "Up"

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_gnpsalignment(spectrum1_dict, spectrum2_dict, alignment_params={}):
    calculate_gnps = memory.cache(run_gnps.calculate_gnps)
    score = calculate_gnps(spectrum1_dict, spectrum2_dict, alignment_params=alignment_params)

    results = {}
    results["sim"] = score["score"]
    results["type"] = "gnpsalignment"

    return results

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_matchms(spectrum1_dict, spectrum2_dict, scoring_function="modified_cosine", alignment_params={}):
    calculate_matchms = memory.cache(run_spec2vec.calculate_matchms)
    score = calculate_matchms(spectrum1_dict, spectrum2_dict, scoring_function=scoring_function, alignment_params=alignment_params)

    results = {}
    results["sim"] = float(score["score"].flat[0])
    results["matched_peaks"] = int(score["matches"].flat[0])
    results["type"] = "matchms:{}".format(scoring_function)

    return results

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_spec2vec(spectrum1_dict, spectrum2_dict, alignment_params={}):
    calculate_spec2vec = memory.cache(run_spec2vec.calculate_spec2vec)
    score = calculate_spec2vec(spectrum1_dict, spectrum2_dict, alignment_params=alignment_params)

    results = {}
    results["sim"] = score
    results["type"] = "spec2vec"

    return results

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_simile(spectrum1_dict, spectrum2_dict, alignment_params={}):
    calculate_simile = memory.cache(run_simile.calculate_simile)
    score = calculate_simile(spectrum1_dict, spectrum2_dict, alignment_params=alignment_params)

    results = {}
    results["sim"] = score["score"]
    results["matched_peaks"] = score["matched_peaks"]
    results["pval"] = score["pval"]
    results["type"] = "simile"

    return results

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_ms2deepscore(spectrum1_dict, spectrum2_dict, alignment_params={}):
    calculate_ms2deepscore = memory.cache(run_ms2deepscore.calculate_ms2deepscore)
    score = calculate_ms2deepscore(spectrum1_dict, spectrum2_dict, alignment_params=alignment_params)

    results = {}
    results["sim"] = score["score"]
    results["type"] = "ms2deepscore"

    return results

@celery_instance.task(time_limit=60)
def tasks_compute_similarity_spectralentropy(spectrum1_dict, spectrum2_dict, alignment_params={}):
    calculate_spectralentropy = memory.cache(run_spectralentropy.calculate_spectralentropy)
    score = calculate_spectralentropy(spectrum1_dict, spectrum2_dict, alignment_params=alignment_params)

    results = {}
    results["sim"] = score["score"]
    results["type"] = "spectralentropy"

    return results


# celery_instance.conf.beat_schedule = {
#     "cleanup": {
#         "task": "tasks._task_cleanup",
#         "schedule": 3600
#     }
# }


celery_instance.conf.task_routes = {
    'tasks.task_computeheartbeat': {'queue': 'worker'},

    
    'tasks.tasks_compute_similarity_gnpsalignment': {'queue': 'worker'},
    'tasks.tasks_compute_similarity_usi': {'queue': 'worker'},

    'tasks.tasks_compute_similarity_spec2vec': {'queue': 'spec2vec'},
    'tasks.tasks_compute_similarity_matchms': {'queue': 'spec2vec'},

    'tasks.tasks_compute_similarity_simile': {'queue': 'simile'},
    'tasks.tasks_compute_similarity_ms2deepscore': {'queue': 'ms2deepscore'},

    'tasks.tasks_compute_similarity_spectralentropy': {'queue': 'worker'},
}