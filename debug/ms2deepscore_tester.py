
import requests
import numpy as np

from matchms import Scores, Spectrum
from matchms.filtering import normalize_intensities
from ms2deepscore import SpectrumBinner
from ms2deepscore.typing import BinnedSpectrumType

def _create_input_vector(binned_spectrum: BinnedSpectrumType, input_vector_dim=9948):
    """Creates input vector for model.base based on binned peaks and intensities"""
    X = np.zeros((1, input_vector_dim))

    idx = np.array([int(x) for x in binned_spectrum.binned_peaks.keys()])
    values = np.array(list(binned_spectrum.binned_peaks.values()))
    X[0, idx] = values
    return X

r = requests.get("https://metabolomics-usi.ucsd.edu/json/?usi=mzspec%3AGNPS%3ATASK-c95481f0c53d42e78a61bf899e9f9adb-spectra%2Fspecs_ms.mgf%3Ascan%3A1943")
my_spectrum = r.json()

print(my_spectrum)

number_of_bins = 9948
mz_max = 1000.0
mz_min = 10.0
spectrum_binner = SpectrumBinner(number_of_bins, mz_min=mz_min, mz_max=mz_max, peak_scaling=0.5)

metadata1 = {"precursor_mz": my_spectrum["precursor_mz"]}

mz1 = [peak[0] for peak in my_spectrum["peaks"]]
int1 = [peak[1] for peak in my_spectrum["peaks"]]

s1 = Spectrum(np.array(mz1), np.array(int1), metadata1)

binned_spectrums = spectrum_binner.fit_transform([s1])

#binned1 = spectrum_binner.transform([s1])[0]

print(_create_input_vector(binned_spectrums[0])[0].tolist())
