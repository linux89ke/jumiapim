import pandas as pd
import streamlit as st
from datetime import datetime
import string
import logging
import zipfile
import os

# Function to split and save Excel file
def split_and_save_excel(input_file, max_rows=9800):
    # Read the input Excel file
    try:
        excel_file = pd.ExcelFile(input_file)
    except pd.errors.ExcelFileError as e:
        logging.error(f"Error reading Excel file: {e}")
        return

    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime("%Y-%m-%d")

    output_files = []

    for sheet_name in excel_file.sheet_names:
        # Skip the "RejectionReasons" sheet
        if sheet_name == 'RejectionReasons':
            continue

        # Read the sheet into a DataFrame
        df = excel_file.parse(sheet_name)

        # Split the DataFrame into smaller DataFrames based on the specified maximum rows
        smaller_dfs = [df.iloc[i:i + max_rows] for i in range(0, len(df), max_rows)]

        for i, smaller_df in enumerate(smaller_dfs):
            # Get the alphabetical numbering (A, B, C, ...)
            numbering = string.ascii_uppercase[i % 26]

            # Construct the output file name
            output_file_name = f"KE_PIM_{current_date}_{sheet_name}_Set{i + 1}.xlsx"

            # Save the current sheet
            smaller_df.to_excel(output_file_name, index=False)

            output_files.append(output_file_name)

    logging.info(f"Saved {len(output_files)} files.")
    return output_files

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit UI
st.title("Excel File Splitter")

# File upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Display filename
    st.write("Uploaded file:", uploaded_file.name)

    # Split Excel file and get list of output files
    output_files = split_and_save_excel(uploaded_file)

    # Display progress
    st.write("Splitting complete! Number of output files:", len(output_files))

    # List output files with download links
    st.write("Output Files:")
    for file in output_files:
        st.write(file)
        with open(file, "rb") as f:
            st.download_button(label="Download", data=f, file_name=file)

    # Download all files as a zip
    if st.button("All Files (Zipped)"):
        with st.spinner("Zipping files..."):
            zip_file_name = "output_files.zip"
            with zipfile.ZipFile(zip_file_name, "w") as zipf:
                for file in output_files:
                    zipf.write(file)
            with open(zip_file_name, "rb") as f:
                st.download_button(label="Download", data=f, file_name=zip_file_name)
            # Remove the zip file after download
            os.remove(zip_file_name)
