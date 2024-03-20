import pandas as pd
import streamlit as st
from datetime import datetime
import string
import logging
import zipfile
import os

# Function to split and save Excel file
def split_and_save_excel(input_file, max_rows=9800):
    try:
        excel_file = pd.ExcelFile(input_file)
    except pd.errors.ExcelFileError as e:
        logging.error(f"Error reading Excel file: {e}")
        st.error("Error reading Excel file. Please make sure it's a valid Excel file.")
        return []

    current_date = datetime.now().strftime("%Y-%m-%d")
    output_files = []

    for sheet_name in excel_file.sheet_names:
        # Skip splitting RejectionReasons sheet
        if sheet_name == 'RejectionReasons':
            continue
        
        # Read ProductSets sheet
        df = excel_file.parse(sheet_name)
        df_chunks = [df[i:i+max_rows] for i in range(0, len(df), max_rows)]

        for i, chunk in enumerate(df_chunks):
            output_file_name = f"KE_PIM_{current_date}_{sheet_name}_Set{i + 1}.xlsx"
            # Write to Excel file with ProductSets sheet
            with pd.ExcelWriter(output_file_name, engine='xlsxwriter') as writer:
                chunk.to_excel(writer, sheet_name=sheet_name, index=False)
                # Clone RejectionReasons sheet
                excel_file.parse('RejectionReasons').to_excel(writer, sheet_name='RejectionReasons', index=False)
            output_files.append(output_file_name)

    logging.info(f"Saved {len(output_files)} files.")
    return output_files

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit UI
st.title("Excel File Splitter")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.write("Uploaded file:", uploaded_file.name)
    output_files = split_and_save_excel(uploaded_file)

    if len(output_files) > 0:
        st.write("Splitting complete! Number of output files:", len(output_files))

        st.write("Output Files:")
        for file in output_files:
            st.write(file)
            with open(file, "rb") as f:
                st.download_button(label="Download", data=f, file_name=file)

        if st.button("All Files (Zipped)"):
            with st.spinner("Zipping files..."):
                zip_file_name = "output_files.zip"
                with zipfile.ZipFile(zip_file_name, "w") as zipf:
                    for file in output_files:
                        zipf.write(file)
                with open(zip_file_name, "rb") as f:
                    st.download_button(label="Download", data=f, file_name=zip_file_name)
                os.remove(zip_file_name)
    else:
        st.error("No valid output files were generated.")
