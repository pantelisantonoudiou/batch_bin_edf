# EEG_EDF
Batch conversion of EEG to EDF files

# Dependancies:

1) NumPy

2) Pandas

3) tqdm

4) PyEDFlib - (https://pyedflib.readthedocs.io)

# Modules:

file_check.py 

              - contains function to test if your multi-channel EEG files are in the proper format for EEG conversion

              - contains function for deleting convered EDF files that are smaller than a threshold
              

EDF_routines.py 

               - converts EEG to EDF files
