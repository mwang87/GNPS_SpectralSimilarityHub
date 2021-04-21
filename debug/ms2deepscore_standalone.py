import numpy as np
import pandas as pd
import requests
import json

from ms2deepscore import MS2DeepScore
from ms2deepscore import SpectrumBinner
from ms2deepscore.models import SiameseModel, load_model
from matchms import Scores, Spectrum
from matchms.filtering import normalize_intensities

model_file = "../bin/ms2deepscore/ms2deepscore_model.hdf5"
model = load_model(model_file)

r = requests.get("https://metabolomics-usi.ucsd.edu/json/?usi=mzspec%3AGNPS%3ATASK-c95481f0c53d42e78a61bf899e9f9adb-spectra%2Fspecs_ms.mgf%3Ascan%3A1943")
my_spectrum = r.json()

metadata1 = {"precursor_mz": my_spectrum["precursor_mz"]}

mz1 = [peak[0] for peak in my_spectrum["peaks"]]
int1 = [peak[1] for peak in my_spectrum["peaks"]]

s1 = Spectrum(np.array(mz1), np.array(int1), metadata1)

print(s1)
similarity_measure = MS2DeepScore(model)
binned_spectrums = similarity_measure.model.spectrum_binner.transform([s1])
my_vector = similarity_measure._create_input_vector(binned_spectrums[0])

query_dict = {}
query_dict["input_a"] = my_vector.tolist()[0]
query_dict["input_b"] = my_vector.tolist()[0]

pred_url = "http://localhost:8501/v1/models/MS2DEEPSCORE:predict"
payload = json.dumps({"instances": [ query_dict ]})

headers = {"content-type": "application/json"}
json_response = requests.post(pred_url, data=payload, headers=headers)

print(json_response.json())
print(json_response.json()["predictions"][0])
#score = similarity_measure.pair(s1, s1)
#print(score)
