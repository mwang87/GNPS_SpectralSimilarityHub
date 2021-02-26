import os
import sys
import gensim
import numpy as np
import pandas as pd

from matchms.filtering import normalize_intensities
from matchms.filtering import require_minimum_number_of_peaks
from matchms.filtering import select_by_mz
from matchms.filtering import select_by_relative_intensity
from matchms.filtering import reduce_to_number_of_peaks
from matchms.filtering import add_losses
from matchms.importing import load_from_mgf
from matchms import calculate_scores
from matchms import Scores, Spectrum
from matchms.similarity import ModifiedCosine


def calculate_modified_cosine(spectrum1_dict, spectrum2_dict):
    metadata1 = {"precursor_mz": spectrum1_dict["precursor_mz"]}
    metadata2 = {"precursor_mz": spectrum2_dict["precursor_mz"]}

    mz1 = [peak[0] for peak in spectrum1_dict["peaks"]]
    int1 = [peak[1] for peak in spectrum1_dict["peaks"]]

    mz2 = [peak[0] for peak in spectrum2_dict["peaks"]]
    int2 = [peak[1] for peak in spectrum2_dict["peaks"]]

    s1 = Spectrum(np.array(mz1), np.array(int1), metadata1)
    s2 = Spectrum(np.array(mz2), np.array(int2), metadata2)

    norm_s1 = normalize_intensities(s1)
    norm_s2 = normalize_intensities(s2)
    modified_cosine = ModifiedCosine()
    score = modified_cosine.pair(norm_s1, norm_s2)

    return score

def calculate_spec2vec(spectrum1_dict, spectrum2_dict):
    metadata1 = {"precursor_mz": spectrum1_dict["precursor_mz"]}
    metadata2 = {"precursor_mz": spectrum2_dict["precursor_mz"]}

    mz1 = [peak[0] for peak in spectrum1_dict["peaks"]]
    int1 = [peak[1] for peak in spectrum1_dict["peaks"]]

    mz2 = [peak[0] for peak in spectrum2_dict["peaks"]]
    int2 = [peak[1] for peak in spectrum2_dict["peaks"]]

    s1 = Spectrum(np.array(mz1), np.array(int1), metadata1)
    s2 = Spectrum(np.array(mz2), np.array(int2), metadata2)

    norm_s1 = normalize_intensities(s1)
    norm_s2 = normalize_intensities(s2)

    return 0