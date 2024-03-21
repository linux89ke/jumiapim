import streamlit as st
import pandas as pd
import os
import csv

def detect_delimiter(file):
    # Read a sample of the file to detect the delimiter
    sample = file.read(1024)
    file.seek(0)  # Reset file pointer to beginning
    # Use CSV Sniffer to detect delimiter
    dialect = csv.Sniffer().sniff(sample)
    return dialect.delimiter

def merge_csv_files(output_file, uploaded_files):
    delimiters = set()
    merged_dfs = []
    for file in uploaded_files:
        delimiter = detect_delimiter(file)
        delimiters.add(delimiter)
        merged_df = pd.read_csv(file, delimiter=delimiter)
        merged_dfs.append(merged_df)
    if len(delimiters) > 1:
        st.warning("Uploaded files have different delimiters. Please ensure all files have the same delimiter.")
        return None
    merged_df = pd.concat(merged_dfs, ignore_index=True)
    
    # Add blank columns for SellerID and Category
    merged_df["SellerID"] = ""
    merged_df["Category"] = ""
    
    return merged_df

def main():
    st.title("CSV File Merger")

    # Allow user to upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files to merge", accept_multiple_files=True)

    if uploaded_files:
        output_file = "merged_file.csv"

        # Merge the uploaded CSV files
        merged_df = merge_csv_files(output_file, uploaded_files)

        if merged_df is not None:
            # Select only specific columns
            selected_columns = ["SellerName", "Name", "Brand", "PrimaryCategory", "SellerID", "Category"]
            merged_df = merged_df[selected_columns]

            # Save the selected columns to a CSV file
            merged_df.to_csv(output_file, index=False)

            # Offer download link for the merged CSV file
            st.markdown(f"### [Download merged CSV file]({output_file})")

            # Download button for the merged CSV file
            st.download_button(label="Download merged CSV file", data=open(output_file, "rb").read(), file_name=os.path.basename(output_file), mime="text/csv")

if __name__ == "__main__":
    main()
