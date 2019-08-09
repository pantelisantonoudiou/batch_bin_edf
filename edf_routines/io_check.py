# -*- coding: utf-8 -*-
"""  Checks file size and format of time-series data for EDF conversion

Contains 4 functions:

1) get_file_size() - gets file size across days for one subject -subroutine
2) df_to_excel_form() - save dataframe as excel and format -subroutine
3) file_check_main() - Returns dataframe with file properties and saves excel file in bin_path -Main
4) file_del(paths,thresh) - Deletes edf files smaller than threhold

e.g.
# run to check files before EDF conversion- get dataframe and excel output
df = file_check_main(paths,fs)

# run to delete files converted EDF files that are too small
file_del(paths,thresh)


Created on Mon Aug  5 15:17:36 2019
@author: Pantelis Antonoudiou
"""


# --------------------------------------------------------------------------  #

# Import libraries
import os
import numpy as np
import pandas as pd
from tqdm import tqdm  
import string
import pdb
# --------------------------------------------------------------------------  #
    
# get file size to check for consistency
def get_file_size(paths,fs):
    """ get_file_size(bin_path,fs)
    returns a 2D list with the time of file size for all subfolders of each subject 
    first element = subfolder_name (Day)
    second element = file duration (Hours)
    """
    # get path
    bin_path = os.path.join(paths['bin_path'], paths['subject_id'])
    
    # create empty list
    list1 = []; 
    
    # get day directory
    dir1 = os.listdir(os.path.join(bin_path))
        
    for i in range(len(dir1)):
        
        # get day directory
        file_dir = os.listdir(os.path.join(bin_path,dir1[i]))
        
        # empty list
        file_size = []
        
        for ii in range(len(file_dir)): # loop through files
            # get path
            file = os.path.join(bin_path, dir1[i], file_dir[ii])
            
            # get file size
            os.path.getsize(file)
            
            # store file size
            file_size.append (os.path.getsize(file)/2/fs/3600)
        
        # are all elements equal?
        same_size = len(set(file_size)) <= 1
            
        # append day to list
        list1.append([dir1[i], min(file_size), len(file_size), same_size]) 
        
        # sort list
        list1.sort()
         
    return(list1)
# --------------------------------------------------------------------------  #       
   
# save dataframe in a formatted excel format         
def df_to_excel_form(save_path,df,config):
    """ df_to_excel_form(save_path,df)
    Deletes files smaller than threshold
    """
    
    # set column for formatting
    cols = ['Files_equal?', 'Files', 'Min_fl_size(Hours)']
    
    # get length of df
    len_df = str(len(df.index) + 1)
    
    # get criteria, values and lists    
    criteria =['not containing', '<', '<']
    values = ['True', len(config['ch_id']), 1]
    types = ['text', 'cell', 'cell']
   
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(os.path.join(save_path,'file_check.xlsx'), engine='xlsxwriter')
    
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
    
    # create condition list
    cond = []
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
        
        # verify if conditions were true 
        cond.append(all(df[cols[i]] == values[i]))
    
    # correct last statement
    cond[i] = all(df[cols[i]] > values[i])
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    return cond

          
# --------------------------------------------------------------------------  #

# check files before EDF conversion
def file_check_main(paths,config):
    """ file_check_main(paths,fs,config)
    """
    # get fs
    fs = config['fs']
    
    # create dataframe
    df = pd.DataFrame(columns = ['Subject_ID','Day','Min_fl_size(Hours)','Files','Files_equal?'])
    
    # veirfy that loading path exists
    if not os.path.exists(paths['bin_path']):
        print('Loading path does not exist')
        return
    
    # get subject directory
    subject_dir = [dI for dI in os.listdir(paths['bin_path']) if os.path.isdir(os.path.join(paths['bin_path'],dI))]
    pdb.set_trace
    # loop through subjects
    for i in tqdm(range(0,len(subject_dir))):
        
        # update paths
        paths.update({'subject_id' : subject_dir[i]})
          
        # file size
        day_list = get_file_size(paths,fs)    
        
        # append day to dataframe
        save_array = np.array(day_list)
        
        # pass list to array
        dftemp = pd.DataFrame({'Subject_ID':paths['subject_id'], 'Day':save_array[:,0].astype(np.float), 'Min_fl_size(Hours)':save_array[:,1].astype(np.float),
                               'Files':save_array[:,2].astype(np.float), 'Files_equal?':save_array[:,3] })
        # concatenate array
        df = pd.concat([df, dftemp],ignore_index=True)
        
    # save to excel
    save_path = paths['bin_path'][0:paths['bin_path'].rfind('/')]
    cond = df_to_excel_form(save_path,df,config)
    
    if all(cond) is True:
        print('Files are ready for EDF conversion.')
    else:
        print('Files are not formatted properly! please check file_check.xlsx.')
        
    # return dataframe           
    return df

# --------------------------------------------------------------------------  #

# delete files smaller than a threshold    
def file_del(paths,config):
    """ file_del(paths,thresh)
    """
    # get size threshold
    thresh = config['size_thresh']
  
    # veirfy that loading path exists
    if not os.path.exists(paths['edf_path']):
        print('Save path does not exist')
        return
    
    # get subject directory
    subject_dir = [dI for dI in os.listdir(paths['edf_path']) if os.path.isdir(os.path.join(paths['edf_path'],dI))]
    
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
            
# --------------------------------------------------------------------------  #


        

            