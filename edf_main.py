# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 09:40:36 2019

@author: panton01
"""

# Imports
import json,sys
from edf_routines import io_check
from edf_routines import bin_edf

# Load config file 
try:
    config = open('config.json', 'r').read()
    config = json.loads(config)
except Exception as err:
    raise FileNotFoundError(f"Unable to read the config file.\n{err}")
     
# check config
print(config)

# get arguments
if len(sys.argv)<2:
    raise Exception('Option missing e.g. python edf_del')
                    
    
option = sys.argv[1]
      
if option not in ['edf_del','file_check', 'bin_edf']:
    raise Exception(f"No valid option provided: 'edf_del','file_check', 'bin_edf'. \n'{option}' was provided instead.")


# gather paths in a dict
paths = {'bin_path': config['bin_path'], 'edf_path' :config['edf_path']} 

# remove last slash if exists
if paths['bin_path'].rfind('/')-len(paths['bin_path']) is -1:    
      paths.update({'bin_path' : paths['bin_path'][0:len(paths['bin_path'])-1]})
      
if paths['edf_path'].rfind('/')-len(paths['edf_path']) is -1:    
      paths.update({'edf_path' : paths['edf_path'][0:len(paths['edf_path'])-1]})


if option == 'edf_del':
    io_check.file_del(paths,config['size_thresh'])
elif option == 'file_check':
    io_check.file_check_main(paths,config['fs'])
elif option == 'bin_edf':
    bin_edf.lfp_edf_main(paths,config['fs'],config['time_bin'])    
