# PNL-coding-test

This repository contains the implementation of the two tasks (arithmatic and neuroimaging) in the coding test at PNL interview. Output files from both tasks can be found in the output_files directory. Workflows can be found in the notebook under the name bioinform-test.ipynb.

#### Environment setup
Install the dependencies:
```sh setup.sh```

---
### Task 1

This task aimed at anonymizing participants' privacy information in a dataset. 

##### Run the pipeline:
```python3 task1.py [dowload path] [upload path] [filename] [TOKEN]```

The pipeline consists of the following parts:

*API and Token*
* Register a dropbox account, generate a token following [OAuth guide](https://developers.dropbox.com/oauth-guide)
* Connect to Dropbox using access token

*Download*
```download_and_readCSV(dbx, path)```
* Download the provided dataset via Dropbox API from the file path (download path + filename) 
* Read byte data to string, load as DataFrame

*Find Age*
```age_when_consent(df, birth_col, consent_col)```
* Calculate the age of participants at date of consent
* DoC - birthdate, in datetime
* Replace the birthday column with age


*Anonymize*
```disguise_DoC(df, col, end_date, max_n)```
* Generate random numbers of day (offset) greater than the days between today and 1925-01-01, save as a separate dataframe
* Find the extact dates based on the randomized days offset
* Replace the original DoC column with the disguised one

*Upload*
```save_and_upload(dbx, df, offset, filename1, filename2, local_out, upload_path)```
* Save dataframes to local path
* From local, uplad to the corresponding Dropbox path in arguments


### Task 2

This task aimed at computing volumes of different brain regions. To do so, we have to first superimpose a given T1w image upon an standard image whose region boundaries are known utilizing the ANTs package. 

##### Run the pipeline:
```python3 task2.py```

The pipeline consists of the following parts:

*Calculate volumes of brain parts*
```find_volume(label_data, reg_data)```
* For each type of label, binarize the atlas in label region and multiply with the registered image
* Count the number of non-zeros in the multiplied matrix to find volume
* Save label-volume combinations to a dataframe

*Process lookup table*
```process_raw_FS(raw_txt)```
* Save the raw FreeSurfer lookup table directly from the [website](https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT)
* Extract lines start with numbers in the raw text
* Read the cleaned text into dataframe and keep the first two columns only

*Join tables*
* Join the free surfer dataframe with the brain volume dataframe on identical labels
* Save to local


