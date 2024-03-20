import pandas as pd
import streamlit as st
from datetime import datetime
import string
import logging
import zipfile
import os

# Function to split and save Excel file
def split_and_save_excel(input_file, chunk_size=9998):
    try:
        excel_file = pd.ExcelFile(input_file)
    except pd.errors.ExcelFileError as e:
        logging.error(f"Error reading Excel file: {e}")
        st.error("Error reading Excel file. Please make sure it's a valid Excel file.")
        return [], 0

    # Get total number of rows in the input file
    total_rows = 0
    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)
        total_rows += len(df)

    # Display total number of rows
    st.write(f"Total number of rows in input file: {total_rows}")

    # Slider for choosing chunk size
    chunk_size = st.slider("Choose number of rows per chunk", min_value=6500, max_value=9998, value=chunk_size)

    current_date = datetime.now().strftime("%Y-%m-%d")
    output_files = []

    if st.button("Split Files"):
        # Progress bar
        progress_bar = st.progress(0)

        progress_value = 0
        progress_increment = 100 / total_rows

        for sheet_name in excel_file.sheet_names:
            if sheet_name == 'RejectionReasons':
                continue
            
            df = excel_file.parse(sheet_name)
            df_chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

            for i, chunk in enumerate(df_chunks):
                output_file_name = f"KE_PIM_{current_date}_{sheet_name}_Set{i + 1}.xlsx"
                with pd.ExcelWriter(output_file_name, engine='xlsxwriter') as writer:
                    chunk.to_excel(writer, sheet_name=sheet_name, index=False)
                    excel_file.parse('RejectionReasons').to_excel(writer, sheet_name='RejectionReasons', index=False)
                output_files.append(output_file_name)

                # Update progress bar
                progress_value += progress_increment
                progress_bar.progress(progress_value)

        logging.info(f"Saved {len(output_files)} files.")

    return output_files, total_rows

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit UI
st.title("Excel File Splitter")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.write("Uploaded file:", uploaded_file.name)
    output_files, total_rows = split_and_save_excel(uploaded_file)

    if st.button("All Files (Zipped)") and len(output_files) > 0:
        with st.spinner("Zipping files..."):
            zip_file_name = "output_files.zip"
            with zipfile.ZipFile(zip_file_name, "w") as zipf:
                for file in output_files:
                    zipf.write(file)
            with open(zip_file_name, "rb") as f:
                st.download_button(label="Download Zip", data=f, file_name=zip_file_name)
            os.remove(zip_file_name)
