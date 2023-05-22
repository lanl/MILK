#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import pandas as pd
from pathlib import Path

def read_file(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines

def write_file(lines, ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)

def remove_intensity(lines):
    indStart = []
    indEnd = []
    for ind in range(0, len(lines)):
        line = lines[ind]
        if "#custom_object_intensity_data" in line:
            indStart.append(ind)

        if "#end_custom_object_intensity_data" in line:
            indEnd.append(ind+1)

    # Remove in reverse order
    for ind in reversed(range(0, len(indStart))):
        del lines[indStart[ind]:indEnd[ind]]

    return lines

def swap_datasets(lines, datasets):
    #Assume that all dataset files have the same extension
    ext = Path(datasets[0]).suffix

    # Find a list of datasets already in the template
    datasetsold = []
    datasetInd = []
    for ind in range(0, len(lines)):
        line = lines[ind]
        if ext in line:
            datasetInd.append(ind)
            tmp = line.split('subordinateObject_')[-1]
            tmp = tmp.split(' ')[-1]
            tmp = tmp.replace("'", '')
            datasetsold.append(tmp.split(ext)[-2]+ext)

    # Get the unique datasets make sure datasets make sense
    datasetsold = sorted(set(datasetsold))
    assert len(datasetsold) == len(datasets), 'The length of datasets were not the same!'

    # Loop over the datasets and copy in the new file names
    for ind in datasetInd:
        line = lines[ind]
        for ind2 in range(0, len(datasetsold)):
            if datasetsold[ind2] in line:
                line = line.replace(datasetsold[ind2], datasets[ind2])
        lines[ind] = line
    return lines

def split_list_of_str(listofstr):
    tmp  = listofstr.replace('[','')
    tmp  = tmp.replace(']','')
    tmp  = tmp.replace('\'','')
    tmp  = tmp.replace(',','')
    return tmp.split(' ')

def main(filename: str = "dataset.csv", work_dir: Path = Path.cwd(), keep_intensity: bool = True):
    df = pd.read_csv(filename)
    db = df.to_dict(orient='list')

    # Make directory specified by path (if doesn't exist) and copy in the data files
    for data_files_tmp,data_dir,folder,ifile,ofile in zip(db["data_files"],db["data_dir"],db["folder"],db["ifile"],db["ofile"]):
        data_files = split_list_of_str(data_files_tmp)

        target_dir = work_dir / folder
        target_dir.mkdir(parents=True,exist_ok=True)
        for file in data_files:
            shutil.copyfile(Path(data_dir) / file, target_dir / file)

        # Readin the template file
        linesTfile = read_file(ifile)

        # Remove intensity data if appropriate
        if not keep_intensity:
            linesTfile = remove_intensity(linesTfile)

        # detect the current dataset names and replace with new dataset names
        linesTfile = swap_datasets(linesTfile, data_files)

        # Write the parameter file to the directory
        write_file(linesTfile, target_dir / ofile)

if __name__ == '__main__':
    main()
