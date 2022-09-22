import dropbox
import argparse
import pandas as pd
import numpy as np
from io import StringIO
from datetime import date, datetime, timedelta
import random

parser = argparse.ArgumentParser(description='Download and Upload')
parser.add_argument('download_folder', type=str, help='Folder (including subfolders if applicable) where to download')
parser.add_argument('upload_folder', type=str, help='Folder (including subfolders) where to upload')
parser.add_argument('file_name', type=str)
parser.add_argument('token', type=str, help='Dropbox access token')

def download_and_readCSV(dbx, path):
    '''
    This function downloads file and load as dataframe from given path through Dropbox API
    '''

    try:
    #download file
        md, res = dbx.files_download(path)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None

    #read byte to string
    s = str(res.content, 'utf-8')
    data = StringIO(s)
    #load string to dataframe
    df = pd.read_csv(data)

    return df

def age_when_consent(df, birth_col, consent_col):
    '''
    This function calculate the ages of participants at date of consent
    '''

    # transfer string columns (birthday and DoC) to datetime
    birthd = pd.to_datetime(df[birth_col], format = '%Y-%m-%d')
    constd = pd.to_datetime(df[consent_col], format = '%m/%d/%Y')

    # age in number of days at consent
    age_in_days = (constd - birthd).dt.days
    # age in years (i.e. 36.5 years old -> 36 years old)
    df['age'] = np.floor(age_in_days / 365).astype(int)

    df = df.drop(birth_col, axis = 1)
    return df

def disguise_DoC(df, col, end_date, max_n):
    '''
    This function returns a dataframe with disguised date of consent 
    and a corresponding dataframe of number of days (offset)
    '''

    today = datetime.today()
    strt_day = pd.to_datetime(end_date)

    # diff in days between 1925-01-01 and today
    diff_days = (today - strt_day).days

    # randomize num of days offset
    days_offset = []
    for i in range(0, df.shape[0]):
        days_offset += [random.randint(0, max_n) + diff_days]
        
    # store days offset as dataframe
    offset_df = pd.DataFrame(days_offset, columns = ['days_offset'])

    # create a new column for DoC by finding number of days (offset) before today
    df[col] = offset_df['days_offset'].apply(lambda x: today - timedelta(x))
    df[col] = pd.to_datetime(df[col]).dt.strftime('%-m/%-d/%Y')

    return df, offset_df

def save_and_upload(dbx, df, offset, filename1, filename2, local_out, upload_path):
    '''
    save dataframes to local path, from where upload to dropbox
    '''

    #save dataframes to localpath
    df.to_csv(local_out+'/'+filename1, index = False)
    offset.to_csv(local_out+'/'+filename2, index = False)

    #upload to dropbox
    with open(local_out+'/'+filename1, 'rb') as f:    
        meta1 = dbx.files_upload(f.read(), upload_path+'/'+filename1, 
                                mode=dropbox.files.WriteMode("overwrite"))
    
    with open(local_out+'/'+filename2, 'rb') as f:    
        meta2 = dbx.files_upload(f.read(), upload_path+'/'+filename2, 
                                mode=dropbox.files.WriteMode("overwrite"))
    

def main():

    #parse arguments
    args = parser.parse_args()
    downfolder = args.download_folder
    upfolder = args.upload_folder
    file = args.file_name
    TOKEN = args.token

    downpath = downfolder + '/' + file

    #local path to save outputs and filenames
    local_outpath = 'output_files'
    filename1 = 'enroll_data_anon_YT.csv'
    filename2 = 'enroll_data_offset_YT.csv'

    #connect to dropbox using access token
    dbx = dropbox.Dropbox(TOKEN)

    #download file and load as csv
    df = download_and_readCSV(dbx, downpath)

    #calculate age
    df = age_when_consent(df, 'birth date', 'date of consent')

    #disguise date of consent and find days offset
    df, offset = disguise_DoC(df, 'date of consent', '1925-01-01', 30000)

    save_and_upload(dbx, df, offset, filename1, filename2, local_outpath, upfolder)
    

if __name__ == '__main__':
    main()

