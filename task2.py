import pandas as pd
import nibabel as nib
import numpy as np
import re

# The registration step was fulfilled locally utilizting antsRegistration from ANTs package

def find_volume(label_data, reg_data):
    # find unique labels in label data
    values, counts = np.unique(label_data, return_counts=True)

    # for each label, binarize the atlas in label region and multiply with the registered image to find volume
    brain_v = []
    for i in values[1:]:
        binary_label = label_data == i
        volume = np.count_nonzero(binary_label * reg_data)
        brain_v += [[i, volume]]

    # save label-volume combinations to a dataframe
    brain_v_df = pd.DataFrame(brain_v, columns = ['label', 'volume'])
    return brain_v_df

def process_raw_FS(raw_txt):

    # open the raw FreeSurfer text downloaded directly from the web
    # extract only lines start with numbers 
    with open(raw_txt, 'r') as f1:
        with open('FS.txt', 'w') as f2:
            for line in f1:
                if re.match(r'^\d+', line):
                    f2.write(line)
    
    # read the cleaned txt into dataframe
    fs_df = pd.read_csv('FS.txt', delim_whitespace=True, header = None)
    # keep first two columns
    brain_label = fs_df.iloc[1:, 0:2].set_axis(['label', 'name'], axis = 1)
    
    return brain_label

def main():
    # load and read registered data
    reg = nib.load('brain_data/registered_Warped.nii.gz')
    reg_data = reg.get_fdata()

    #load and read label data
    label = nib.load('brain_data/atlas-integer-labels.nii.gz')
    label_data = label.get_fdata()

    volume = find_volume(label_data, reg_data)
    brain_label = process_raw_FS('FS_Raw.txt')

    #join free surfer dataframe with the brain volume dataframe on label
    result = pd.merge(brain_label, volume, how="right", on=['label'])

    result.to_csv('output_files/brain_region_volume_YT.csv', index = False)

if __name__ == '__main__':
    main()


