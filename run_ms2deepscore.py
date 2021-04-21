import numpy as np
import pandas as pd

from ms2deepscore import MS2DeepScore
from ms2deepscore import SpectrumBinner
from ms2deepscore.models import SiameseModel, load_model
from matchms import Scores, Spectrum
from matchms.filtering import normalize_intensities


model_file = "./bin/ms2deepscore/ms2deepscore_model.hdf5"
model = load_model(model_file)

number_of_bins = 10000
mz_max = 1000.0
mz_min = 10.0
spectrum_binner = SpectrumBinner(number_of_bins, mz_min=mz_min, mz_max=mz_max, peak_scaling=0.5)


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

    #similarity_measure = MS2DeepScore(model)
    #score = similarity_measure.pair(norm_s1, norm_s2)

    # We need to go out to web api to do this
    binned1 = spectrum_binner.transform([s1])[0]
    binned2 = spectrum_binner.transform([s2])[0]

    print(binned1, binned2)

    query_dict = {}
    query_dict["input_a"] = binned1
    query_dict["input_b"] = binned2

    # Handling SUPERCLASS
    fp_pred_url = "http://ms2deepscore-tf-server:8501/v1/models/MS2DEEPSCORE:predict"
    payload = json.dumps({"instances": [ query_dict ]})

    headers = {"content-type": "application/json"}
    json_response = requests.post(fp_pred_url, data=payload, headers=headers)

    pred_super = np.asarray(json.loads(json_response.text)['predictions'])[0]

    return 0.0
