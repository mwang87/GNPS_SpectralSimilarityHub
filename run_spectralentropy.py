import os
import sys
import uuid
import pandas as pd
import shutil
import numpy as np

sys.path.insert(0, "./SpectralEntropy")
import spectral_entropy

def calculate_spectralentropy(spectrum1_dict, spectrum2_dict, alignment_params={}):
    spec_query = np.array(spectrum1_dict["peaks"], dtype=np.float32)
    spec_reference = np.array(spectrum2_dict["peaks"], dtype=np.float32)

    similarity = spectral_entropy.calculate_entropy_similarity(spec_query, \
        spec_reference, \
        ms2_da=alignment_params.get("peak_tolerance", 0.05))
    print("Entropy similarity:{}.".format(similarity))

    scores = {}
    scores["score"] = similarity

    return scores