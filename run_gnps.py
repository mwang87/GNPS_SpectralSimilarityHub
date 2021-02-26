import os
import sys
import uuid
import pandas as pd
import shutil

def get_mgf_string(spectrum_dict):
    output_lines = []
    output_lines.append("BEGIN IONS")
    output_lines.append("SCANS=" + str(spectrum_dict.get("scan", 1)))
    output_lines.append("PEPMASS=" + str(spectrum_dict.get("precursor_mz", 1)))
    output_lines.append("CHARGE=" + str(spectrum_dict.get("charge", 0)))
    output_lines.append("COLLISION_ENERGY=" + str(spectrum_dict.get("collision_energy", 0)))
    peaks_string = "\n".join(["{} {}".format(peak[0], peak[1]) for peak in spectrum_dict["peaks"]])
    output_lines.append(peaks_string)
    output_lines.append("END IONS")

    return "\n".join(output_lines)

def calculate_gnps(spectrum1_dict, spectrum2_dict):
    temp_folder="./temp/{}".format(str(uuid.uuid4()))
    os.makedirs(temp_folder, exist_ok=True)

    temp_mgf = os.path.join(temp_folder, "temp.mgf")
    temp_aligns = os.path.join(temp_folder, "temp.aligns")
    temp_params = os.path.join(temp_folder, "temp.params")

    main_execmodule = "./bin/gnps/main_execmodule"

    with open(temp_params, "w") as o:
        o.write("ALIGNS_FORMAT={}\n".format("tsv"))
        o.write("MIN_MATCHED_PEAKS={}\n".format(1))
        o.write("TOLERANCE_PEAK={}\n".format(0.5))
        o.write("TOLERANCE_PM={}\n".format(2.0))
        o.write("PAIRS_MIN_COSINE={}\n".format(0.1))
        o.write("MAX_SHIFT={}\n".format("9999"))
        o.write("MIN_RATIO={}\n".format("0.1"))
        o.write("INPUT_SPECTRA_MS2={}\n".format(temp_mgf))

    with open(temp_mgf, "w") as o:
        spectrum1_dict["scan"] = 1
        spectrum2_dict["scan"] = 2

        o.write(get_mgf_string(spectrum1_dict))
        o.write("\n")
        o.write(get_mgf_string(spectrum2_dict))

    cmd = "{} ExecMolecularParallelPairs {} -ccms_output_aligns {} -ccms_INPUT_SPECTRA_MS2 {} -ll 9".format(main_execmodule, 
        temp_params, 
        temp_aligns,
        temp_mgf)

    ret = os.system(cmd)
    
    # Reading the data
    df = pd.read_csv(temp_aligns, sep="\t")

    scores = {}
    scores["score"] = df.to_dict(orient="records")[0]["Cosine"]

    # Clean up
    try:
        shutil.rmtree(temp_folder)
    except:
        pass

    return scores
