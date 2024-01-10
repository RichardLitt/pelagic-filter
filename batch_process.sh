#!/bin/bash

# An example of how to use a batch process on a few different regions

# Specify the folder containing KMZ files
folder_path="Greenland"

# Loop through all KMZ files in the folder
for kmz_file in "$folder_path"/*.kmz; do
    # Extract the filename (without extension) for naming the output files
    filename=$(basename -- "$kmz_file")
    filename_no_ext="${filename%.kmz}"

    # Run the script for each KMZ file
    python3 test.py "$kmz_file" "${filename_no_ext}_output.geojson" "ebd_GL_smp_relNov-2023/ebd_GL_smp_relNov-2023.txt" "${folder_path}/${filename_no_ext}.csv"
done
