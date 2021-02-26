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


def calculate_modified_cosine(spectrum1, spectrum2):
    return 0

def calculate_spec2vec(spectrum1, spectrum2):
    return 0