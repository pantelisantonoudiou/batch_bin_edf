# -*- coding: utf-8 -*-
"""  Checks file size and format of time-series data for EDF conversion

Contains 4 functions:

1) get_file_size() - gets file size across days for one subject -subroutine
2) df_to_excel_form() - save dataframe as excel and format -subroutine
3) file_check_main() - Returns dataframe with file properties and saves excel file in eeg_path -Main
4) file_del(paths,thresh) - Deletes edf files smaller than threhold

e.g.
# run to check files before EDF conversion- get dataframe and excel output
df = file_check_main(paths,Fs)

# run to delete files converted EDF files that are too small
file_del(paths,thresh)


Created on Mon Aug  5 15:17:36 2019
@author: Pantelis Antonoudiou
"""

### **** USER INTERACTION **** ###
## ---- SET PATHS AND PARAMETERS -------------- ##

Fs = float(input("Enter sampling rate (samples/sec): ")); # samples per second
thresh = float(input("Min File size (MB): ")) * 1e6 ; # time - in hours- for each epoch 
eeg_path = input("Enter EEG path: ") #"C:/EEG_data" 
edf_path = input("Enter EDF path: ") #"C:/EDF_data"


## ------------------------------------------ ##

# Import libraries
import os
import numpy as np
import pandas as pd
from tqdm import tqdm  
import string

# gather paths in a dict
paths = {'eeg_path': eeg_path, 'edf_path':edf_path} 
    
# get file size to check for consistency
def get_file_size(paths,Fs):
    """ get_file_size(eeg_path,Fs)
    returns a 2D list with the time of file size for all subfolders of each subject 
    first element = subfolder_name (Day)
    second element = file duration (Hours)
    """
    # get path
    eeg_path = os.path.join(paths['eeg_path'], paths['subject_id'])
    
    # create empty list
    list1 = []; 
    
    # get day directory
    dir1 = os.listdir(os.path.join(eeg_path))
        
    for i in range(len(dir1)):
        
        # get day directory
        file_dir = os.listdir(os.path.join(eeg_path,dir1[i]))
        
        # empty list
        file_size = []
        
        for ii in range(len(file_dir)): # loop through files
            # get path
            file = os.path.join(eeg_path, dir1[i], file_dir[ii])
            
            # get file size
            os.path.getsize(file)
            
            # store file size
            file_size.append (os.path.getsize(file)/2/Fs/3600)
        
        # are all elements equal?
        same_size = len(set(file_size)) <= 1
            
        # append day to list
        list1.append([dir1[i], min(file_size), len(file_size), same_size]) 
        
        # sort list
        list1.sort()
         
    return(list1)
       
   
# save dataframe in a formatted excel format         
def df_to_excel_form(paths,df):
    """ df_to_excel_form(paths,df)
    Deletes files smaller than threshold
    """
    
    # set column for formatting
    cols = ['Files_equal?', 'Files', 'Min_fl_size(Hours)']
    
    # get length of df
    len_df = str(len(df.index) + 1)
    
    # get criteria, values and lists    
    criteria =['containing', '<', '<']
    values = ['False', 3,1 ]
    types = ['text', 'cell', 'cell']
   
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(os.path.join(paths['eeg_path'],'file_check.xlsx'), engine='xlsxwriter')
    
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # set the column width and format.
    worksheet.set_column(1,len(df.columns), 18)
    
    # define formats
    green_format = workbook.add_format({'bg_color':'#b6f261'})
    
    # dict for map excel header, first A is index, so omit it
    d = dict(zip(range(25), list(string.ascii_uppercase)[1:]))
    
    # highlight cells
    for i in range(len(cols)):
        
        # get header 
        excel_header = str(d[df.columns.get_loc(cols[i])])       
        # get range
        rng = excel_header + '2:' + excel_header + len_df 
        # highlight worksheet
        worksheet.conditional_format(rng, {'type': types[i],
                                          'criteria': criteria[i],
                                           'value':     values[i],
                                           'format': green_format})
        
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

          


# check files before EDF conversion
def file_check_main(paths,Fs):
    """ file_check_main(paths,Fs)
    """
    
    # create dataframe
    df = pd.DataFrame(columns = ['Subject_ID','Day','Min_fl_size(Hours)','Files','Files_equal?'])
    
    # veirfy that loading path exists
    if not os.path.exists(paths['eeg_path']):
        print('Loading path does not exist')
        return
    
    # get subject directory
    subject_dir = os.listdir(paths['eeg_path'])  
    
    # loop through subjects
    for i in tqdm(range(0,len(subject_dir))):
        
        # update paths
        paths.update({'subject_id' : subject_dir[i]})
          
        # file size
        day_list = get_file_size(paths,Fs)    
        
        # append day to dataframe
        save_array = np.array(day_list)
        
        # pass list to array
        dftemp = pd.DataFrame({'Subject_ID':paths['subject_id'], 'Day':save_array[:,0].astype(np.float), 'Min_fl_size(Hours)':save_array[:,1].astype(np.float),
                               'Files':save_array[:,2].astype(np.float), 'Files_equal?':save_array[:,3] })
        # concatenate array
        df = pd.concat([df, dftemp],ignore_index=True)
        
    # save to excel
    df_to_excel_form(paths,df)

    # return dataframe           
    return df



# delete files smaller than a threshold    
def file_del(paths,thresh):
    """ file_del(paths,thresh)
    """
  
    # veirfy that loading path exists
    if not os.path.exists(paths['edf_path']):
        print('Save path does not exist')
        return
    
    # get subject directory
    subject_dir = os.listdir(paths['edf_path'])  
    
    # loop through subjects
    for i in tqdm(range(0,len(subject_dir))):
        
        # update paths
        paths.update({'subject_id' : subject_dir[i]})
          
        # get subject path
        subject_path = os.path.join(paths['edf_path'], paths['subject_id'])
        
        # get file directory
        dir1 = os.listdir(subject_path)
         
        # loop through files in each subject
        for i in range(len(dir1)):
            
            # get file size
            file_path = os.path.join(subject_path, dir1[i])
            file_size =  os.path.getsize(file_path)
            
            # delete files smaller than threshold
            if file_size < thresh: 
                print(paths['subject_id'],dir1[i])
                os.remove(file_path)
                
    print ('All files smaller than ', thresh, 'Byte have been deleted!')
            



        

            