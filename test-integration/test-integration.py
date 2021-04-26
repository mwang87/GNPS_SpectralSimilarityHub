import requests
import json

def test_usi_api():
    url = "{}/api/comparison".format("https://gnps-similarity.ucsd.edu")
    params = {}
    params["usi1"] = "mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1943"
    params["usi2"] = "mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1969"
    params["peak_tolerance"] = 0.5

    r = requests.get(url, params=params)
    print(r.json())

def test_peaks_api():
    url = "{}/api/comparison".format("https://gnps-similarity.ucsd.edu")

    spec1 = requests.get("https://metabolomics-usi.ucsd.edu/json/?usi={}".format("mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1943"))
    spec2 = requests.get("https://metabolomics-usi.ucsd.edu/json/?usi={}".format("mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1969"))

    params = {}
    params["spec1"] = json.dumps(spec1.json())
    params["spec2"] = json.dumps(spec2.json())
    params["peak_tolerance"] = 0.5

    r = requests.post(url, data=params)
    print(r.json())