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
from matchms.similarity import ModifiedCosine, CosineGreedy

from spec2vec import Spec2Vec
from spec2vec import SpectrumDocument

# Doing actual spec2vec
model = gensim.models.Word2Vec.load("./bin/spec2vec/spec2vec_UniqueInchikeys_ratio05_filtered_iter_50.model")

def calculate_matchms(spectrum1_dict, spectrum2_dict, scoring_function="modified_cosine", alignment_params={}):
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

    if scoring_function == "modified_cosine":
        score_function = ModifiedCosine(tolerance=float(alignment_params.get("peak_tolerance")))
    elif scoring_function == "cosine_greedy":
        score_function = CosineGreedy(tolerance=float(alignment_params.get("peak_tolerance")))
        
    score = score_function.pair(norm_s1, norm_s2)

    return score

def calculate_spec2vec(spectrum1_dict, spectrum2_dict, alignment_params={}):
    metadata1 = {"precursor_mz": spectrum1_dict["precursor_mz"]}
    metadata2 = {"precursor_mz": spectrum2_dict["precursor_mz"]}

    mz1 = [peak[0] for peak in spectrum1_dict["peaks"]]
    int1 = [peak[1] for peak in spectrum1_dict["peaks"]]

    mz2 = [peak[0] for peak in spectrum2_dict["peaks"]]
    int2 = [peak[1] for peak in spectrum2_dict["peaks"]]

    s1 = Spectrum(np.array(mz1), np.sqrt(np.array(int1)), metadata1)
    s2 = Spectrum(np.array(mz2), np.sqrt(np.array(int2)), metadata2)

    norm_s1 = normalize_intensities(s1)
    norm_s2 = normalize_intensities(s2)

    s1_doc = [SpectrumDocument(norm_s1, n_decimals=2)]
    s2_doc = [SpectrumDocument(norm_s2, n_decimals=2)]

    # Define similarity_function
    spec2vec = Spec2Vec(model=model, intensity_weighting_power=0.5,
                            allowed_missing_percentage=80.0)


    scores = calculate_scores(s1_doc, s2_doc, spec2vec).scores

    return scores[0][0]