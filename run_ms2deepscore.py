import numpy as np
import pandas as pd
import json
import requests

from ms2deepscore import MS2DeepScore
from ms2deepscore import SpectrumBinner
from ms2deepscore.models import SiameseModel, load_model
from matchms import Scores, Spectrum
from matchms.filtering import normalize_intensities

model_file = "/models/ms2deepscore_model.hdf5"
model = load_model(model_file)
similarity_measure = MS2DeepScore(model)

def calculate_ms2deepscore(spectrum1_dict, spectrum2_dict, alignment_params={}):
    metadata1 = {"precursor_mz": spectrum1_dict["precursor_mz"]}
    metadata2 = {"precursor_mz": spectrum2_dict["precursor_mz"]}

    mz1 = [peak[0] for peak in spectrum1_dict["peaks"]]
    int1 = [peak[1] for peak in spectrum1_dict["peaks"]]

    mz2 = [peak[0] for peak in spectrum2_dict["peaks"]]
    int2 = [peak[1] for peak in spectrum2_dict["peaks"]]

    s1 = Spectrum(np.array(mz1), np.array(int1), metadata1)
    s2 = Spectrum(np.array(mz2), np.array(int2), metadata2)

    #norm_s1 = normalize_intensities(s1)
    #norm_s2 = normalize_intensities(s2)

    binned_spectrum1 = similarity_measure.model.spectrum_binner.transform([s1])[0]
    binned_spectrum2 = similarity_measure.model.spectrum_binner.transform([s2])[0]

    my_vector1 = similarity_measure._create_input_vector(binned_spectrum1)
    my_vector2 = similarity_measure._create_input_vector(binned_spectrum2)

    query_dict = {}
    query_dict["input_a"] = my_vector1.tolist()[0]
    query_dict["input_b"] = my_vector2.tolist()[0]

    pred_url = "http://ms2deepscore-tf-server:8501/v1/models/MS2DEEPSCORE:predict"
    payload = json.dumps({"instances": [ query_dict ]})

    headers = {"content-type": "application/json"}
    json_response = requests.post(pred_url, data=payload, headers=headers)
    score = json_response.json()["predictions"][0]

    scores = {}
    scores["score"] = score

    return scores
