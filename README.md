# batch_bin_edf
Batch conversion of binary time-series to -> EDF files

# Dependencies:

    1) NumPy

    2) Pandas

    3) tqdm

    4) [PyEDFlib] - (https://github.com/holgern/pyedflib)
    
    5) Json

# Run:

    1) Download/clone batch_bin_edf repository.
    
    2) Update the parameters (sampling rate, paths ...) in the config.json file.
    
    3) Navigate from command prompt to your local repository and run:
         
         a) $ python edf_main.py file_check         # check input sturcture for edf conversion
         b) $ python edf_main.py bin_edf            # convert binary files to edf
         c) $ python edf_main.py edf_del            # delete edf files smaller than a set threshold

# Inputs:

    - Inputs must be int16 binary files.
    - One folder per subject.
    - One folder for each day of recordings placed in the subJect folder.
    - In the 'day' folder there should be one time-series binary file (no header) per channel.
