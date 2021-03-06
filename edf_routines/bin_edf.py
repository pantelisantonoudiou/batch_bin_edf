# -*- coding: utf-8 -*-
""" Converts int_16 time-series binary files to EDF

Contains 4 functions

1) get_file_size() - gets a list of file duration across days per subject - sub-routine
2) lfp_to_edf() - gathers all channels specified and converts to EDF (modify according to channel) - sub-routine
3) separate_n_save() - separates files accordings to time bins for one day - sub-routine
4) lfp_edf_main() - main function -

eg. fs = 4000; # samples per second
    time_bin = 12; # time - in hours- for each epoch 
    bin_path = "C:/Users/panton01/Desktop/bin_data" # path loading folder
    edf_path = "C:/Users/panton01/Desktop/edf_data" # path to new folder to be saved

# execute main function
    lfp_edf_main(paths,fs,time_bin)

Created on Wed Jul 31 11:08:43 2019
@author: Pantelis Antonoudiou
"""

# Import libraries
import os
import pyedflib
from string import ascii_lowercase
from tqdm import tqdm  
import numpy as np

# --------------------------------------------------------------------------  #    
# get file size for one subject
def get_file_size(bin_path,fs):
    """ get_file_size(bin_path,fs)
    returns a 2D list with the time of file size for all subfolders of each subject 
    first element = subfolder_name (Day)
    second element = file duration (Hours)
    """
    
    # create storage list
    list1 = []
    
    # get day directory
    dir1 = os.listdir(os.path.join(bin_path))
        
    for i in range(len(dir1)):
        
        # get day directory
        file_dir = os.listdir(os.path.join(bin_path,dir1[i]))
        
        # load file
        file = os.path.join(bin_path, dir1[i], file_dir[0])
        fp = np.memmap(file, dtype='int16' ,mode='r')
        
        # append day to list
        list1.append([dir1[i],fp.size/fs/3600]) 
        
        # sort list
        list1.sort()
         
    return(list1)
    
# --------------------------------------------------------------------------  #    
        
def lfp_to_edf(paths,day_path,idx,fs,letter_id,config):
    """ lfp_to_edf(paths,day_path,idx,fs,letter_id,config)
    Converts lfp to EDF across channels
    """
    
    # set channel order
    ch_id = config['ch_id']
    
    # get channel list
    ch_list = list(filter(lambda k: config['file_ext'] in k, os.listdir(os.path.join(paths['bin_path'],paths['subject_id'], day_path))))
    
    # pre allocate empty vectors
    channel_info = [];
    data_list = [];
    
    for i in range(len(ch_list)):
            
        # get files in order
        file = list(filter(lambda k: ch_id[i] in k, ch_list))[0]
        
        # load memory mapped file
        load_name = os.path.join(paths['bin_path'],paths['subject_id'], day_path, file)
        fp = np.memmap(load_name, dtype = config['file_type'] ,mode = 'r')
        
        # pass file into a variable and delete memory mapped object
        data = fp[idx[0]*fs*3600: idx[1]*fs*3600] ; del fp
        
        # append to list for storage - remove mean and scale data
        data_list.append((data - np.mean(data))/config['file_norm'])
        
        # get channel properties
        ch_dict = {'label': ch_id[i], 'dimension': config['dimension'][i], 
                   'sample_rate': fs, 'physical_max': config['physical_max'][i],
                   'physical_min': config['physical_min'][i], 'digital_max': config['digital_max'][i], 
                   'digital_min': config['digital_min'][i], 'transducer': '', 'prefilter':''}
        
        # appent to channel info
        channel_info.append(ch_dict)

    # create data file name + path
    data_file = os.path.join(paths['edf_path'],paths['subject_id'],day_path + '_' + letter_id+'.edf')
    
    # intialize EDF object
    f = pyedflib.EdfWriter(data_file, len(ch_id), file_type = pyedflib.FILETYPE_EDF) 
    
    # write file to EDF object
    f.setSignalHeaders(channel_info)
    f.writeSamples(data_list)

    # close and delete EDF object
    f.close()
    del f            
            
# --------------------------------------------------------------------------  #    
    
# save files separated by time bin
def separate_n_save(paths,day_list,fs,time_bin,config):
    """ separate_n_save(paths,day_list,fs,time_bin,config)
    """
    
    for i in tqdm(range(len(day_list))): # loop through days
        
       loops = int(day_list[i][1] / time_bin)  # get loops  
       start_idx = 0;
       
       for ii in range(loops): # loop through file epochs
            
           # convert lfp epochs to edf
           lfp_to_edf(paths, day_list[i][0], [start_idx, start_idx + time_bin], fs ,ascii_lowercase[ii],config)
           
           # update index
           start_idx += time_bin
       
       # convert lfp epoch smaller than time_bin to edf
       last_bin = int(day_list[i][1] % time_bin)
       lfp_to_edf(paths, day_list[i][0], [start_idx, start_idx + last_bin], fs ,ascii_lowercase[ii+1],config)
       
 
# --------------------------------------------------------------------------  #
            
# lfp to edf main program
def lfp_edf_main(paths,config):
    """ lfp_edf_main(paths,config)
    """
    # unpack config parameters
    fs = config['fs']
    time_bin = config['time_bin']
    
    # veirfy that loading path exists
    if not os.path.exists(paths['bin_path']):
        print('Loading path does not exist')
        return
    
    # create save directory if it does not exist
    if not os.path.exists(paths['edf_path']):
        os.makedirs(paths['edf_path'])
       
    # get subject directory
    subject_dir = [dI for dI in os.listdir(paths['bin_path']) if os.path.isdir(os.path.join(paths['bin_path'],dI))]
    
    # loop through subjects
    for i in range(0,len(subject_dir)):
        
        # create directory
        if not os.path.exists(os.path.join(paths['edf_path'],subject_dir[i])):
            os.mkdir(os.path.join(paths['edf_path'],subject_dir[i]))
        
        # update paths
        paths.update({'subject_id' : subject_dir[i]})
        
        # file size
        day_list = get_file_size(os.path.join(paths['bin_path'],subject_dir[i]),fs)             
        
        # separate and save files for one day       
        separate_n_save(paths, day_list,fs, time_bin, config)
        
        # print when an subject is done
        print('subject ', subject_dir[i], 'done' )































