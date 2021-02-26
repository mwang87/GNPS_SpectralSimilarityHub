import simile.simile as sml
import numpy as np

def calculate_simile(spectrum1_dict, spectrum2_dict, alignment_params={}):
    s1 = spectrum1_dict
    s2 = spectrum2_dict

    # import json
    # s1 = json.loads(s1)
    mz1 = [float(x[0]) for x in s1['peaks']]
    i1 = [float(x[1]) for x in s1['peaks']]
    mzi1= np.asarray([mz1,i1])

    # s2 = json.loads(s2)
    mz2 = [float(x[0]) for x in s2['peaks']]
    i2 = [float(x[1]) for x in s2['peaks']]
    mzi2 = np.asarray([mz2,i2])

    # Generate pair-specific substitution matrix
    # S = sml.substitution_matrix(s1[0], s2[0], tolerance=0.01)
    S = sml.substitution_matrix(mzi1[0], mzi2[0], tolerance=alignment_params.get("peak_tolerance", 0.1))

    # Align and score using upper-right quadrant of substitution matrix
    simile_score, simile_alignment1 = sml.pairwise_align(S[:mzi1.shape[1], mzi1.shape[1]:])

    # Calculate significance of the alignment
    pval = sml.alignment_test(S, mzi1[0], mzi2[0])

    scores = {}
    scores["score"] = simile_score
    scores["pval"] = pval

    return scores