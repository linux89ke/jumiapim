import pandas as pd
import streamlit as st
from datetime import datetime
import string
import logging
import zipfile
import os
import math
import base64

# Function to estimate the number of output files
def estimate_output_files(total_rows, chunk_size):
    return math.ceil(total_rows / chunk_size)

# Function to split and save Excel file
def split_and_save_excel(input_file, chunk_size=9998):
    try:
        excel_file = pd.ExcelFile(input_file)
    except pd.errors.ExcelFileError as e:
        logging.error(f"Error reading Excel file: {e}")
        st.error("Error reading Excel file. Please make sure it's a valid Excel file.")
        return [], 0

    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    reject_reasons_file_path = os.path.join(script_directory, "reject reasons.xlsx")

    # Check if the required sheet "ProductSets" is present
    if "ProductSets" not in excel_file.sheet_names:
        st.warning("Input file doesn't have a 'ProductSets' sheet. Creating an empty sheet.")
        product_sets_df = pd.DataFrame(columns=["Placeholder"])
    else:
        # Read the ProductSets sheet
        product_sets_df = excel_file.parse("ProductSets")

    # Read the data from the 'reject reasons.xlsx' file
    if os.path.exists(reject_reasons_file_path):
        reject_reasons_df = pd.read_excel(reject_reasons_file_path)
    else:
        st.error("The 'reject reasons.xlsx' file does not exist.")
        return [], 0

    # Get total number of rows in the input file
    total_rows = 0
    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)
        total_rows += len(df)

    # Display total number of rows
    st.write(f"Total number of rows in input file: {total_rows}")

    # Estimate number of output files based on chunk size
    est_output_files = estimate_output_files(total_rows, chunk_size)
    st.write(f"Estimated number of output files: {est_output_files}")

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
            if sheet_name == 'ProductSets':
                continue
            
            df = excel_file.parse(sheet_name)
            df_chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

            for i, chunk in enumerate(df_chunks):
                output_file_name = f"KE_PIM_{current_date}_{sheet_name}_Set{i + 1}.xlsx"
                with pd.ExcelWriter(output_file_name, engine='xlsxwriter') as writer:
                    chunk.to_excel(writer, sheet_name='ProductSets', index=False)
                    product_sets_df.to_excel(writer, sheet_name='ProductSets', index=False)
                    reject_reasons_df.to_excel(writer, sheet_name='RejectionReasons', index=False)
                output_files.append(output_file_name)

                # Update progress bar
                progress_value += progress_increment
                progress_bar.progress(progress_value)

        logging.info(f"Saved {len(output_files)} files.")

        # Create a zip file
        zip_file_name = f"PIM_Files_{current_date}.zip"
        with zipfile.ZipFile(zip_file_name, "w") as zipf:
            for file in output_files:
                zipf.write(file)

        # Download the zipped file
        with open(zip_file_name, "rb") as f:
            zip_data = f.read()
            b64_zip_data = base64.b64encode(zip_data).decode('utf-8')
            href = f'<a href="data:application/zip;base64,{b64_zip_data}" download="{zip_file_name}">Click here to download the zipped file</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Display individual files as downloadable links
        st.write("Individual Files:")
        for file in output_files:
            st.write(file)
            with open(file, "rb") as f:
                st.download_button(label="Download", data=f, file_name=file)

        # Remove the zip file
        os.remove(zip_file_name)

    return output_files, total_rows

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit UI
st.title("Excel File Splitter")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.write("Uploaded file:", uploaded_file.name)
    output_files, total_rows = split_and_save_excel(uploaded_file)
