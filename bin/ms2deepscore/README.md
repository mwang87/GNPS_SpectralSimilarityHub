## Model Preparation

You will need to download the model with the

```
sh ./get_data.sh
```

Then you will need to convert the keras model into a native tensorflow model that can be served. You will need to create an environment to make this happen. 

```
mamba create -n ms2deepscore python=3.8
mamba install -n ms2deepscore --channel nlesc --channel bioconda --channel conda-forge matchms

pip install ms2deepscore
```