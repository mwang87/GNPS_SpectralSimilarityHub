from ms2deepscore import SpectrumBinner
from ms2deepscore.models import SiameseModel, load_model

model_file = "./bin/ms2deepscore/ms2deepscore_model.hdf5"
model = load_model(model_file)

def calculate_ms2deepscore(spectrum1_dict, spectrum2_dict, alignment_params={}):
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

    similarity_measure = MS2DeepScore(model)
    score = similarity_measure.pair(norm_s1, norm_s2)

    return score
