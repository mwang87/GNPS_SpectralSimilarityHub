import simile.simile as sml
import numpy as np

def calculate_simile(spectrum1_dict, spectrum2_dict):
    mz1 = [peak[0] for peak in spectrum1_dict["peaks"]]
    int1 = [peak[1] for peak in spectrum1_dict["peaks"]]

    s1 = np.asarray([mz1, int1]).astype(float)

    print(s1.shape)

    mz2 = [peak[0] for peak in spectrum2_dict["peaks"]]
    int2 = [peak[1] for peak in spectrum2_dict["peaks"]]

    s2 = np.asarray([mz2, int2]).astype(float)

    print(s2.shape)

    # Generate pair-specific substitution matrix
    S = sml.substitution_matrix(s1, s2, tolerance=.01)

    # Align and score using upper-right quadrant of substitution matrix
    score, alignment = sml.pairwise_align(S[:len(s1),len(s2):])

    # Calculate significance of the alignment
    pval = sml.alignment_test(S, s1, s2)

    scores = {}
    scores["score"] = score
    scores["aligns"] = len(alignment)
    scores["pval"] = pval

    return scores