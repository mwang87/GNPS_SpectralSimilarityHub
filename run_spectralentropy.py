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

    similarity = spectral_entropy.calculate_entropy_similarity(spec_query, spec_reference, ms2_da=0.05)
    print("Entropy similarity:{}.".format(similarity))

    scores = {}
    scores["score"] = similarity    

    return scores


    # print(alignment_params)

    # s1 = spectrum1_dict
    # s2 = spectrum2_dict

    # # import json
    # # s1 = json.loads(s1)
    # mz1 = [float(x[0]) for x in s1['peaks']]
    # i1 = [float(x[1]) for x in s1['peaks']]
    # mzi1= np.asarray([mz1,i1])

    # # s2 = json.loads(s2)
    # mz2 = [float(x[0]) for x in s2['peaks']]
    # i2 = [float(x[1]) for x in s2['peaks']]
    # mzi2 = np.asarray([mz2,i2])

    # # Generate pair-specific substitution matrix
    # # S = sml.similarity_matrix(s1[0], s2[0], tolerance=0.01)
    # S = sml.similarity_matrix(mzi1[0], mzi2[0], tolerance=float(alignment_params.get("peak_tolerance", 0.1)))

    # # Align and score using upper-right quadrant of substitution matrix
    # simile_score, simile_alignment1 = sml.pairwise_align(S[:mzi1.shape[1], mzi1.shape[1]:])

    # # Calculate significance of the alignment
    # pval = sml.significance_test(S, mzi1[0], mzi2[0])

    # scores = {}
    # scores["score"] = simile_score
    # scores["pval"] = pval
    # scores["matched_peaks"] = len(simile_alignment1)
    

    # return scores
