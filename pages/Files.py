import streamlit as st
import pandas as pd
import os
import csv

def detect_delimiter(file):
    # Read a sample of the file to detect the delimiter
    sample = file.read(1024)
    file.seek(0)  # Reset file pointer to beginning
    # Decode the sample bytes to a string
    sample_str = sample.decode('utf-8')
    # Use CSV Sniffer to detect delimiter
    dialect = csv.Sniffer().sniff(sample_str)
    return dialect.delimiter

def merge_csv_files(output_file, uploaded_files):
    dfs = []
    for file in uploaded_files:
        delimiter = detect_delimiter(file)
        dfs.append(pd.read_csv(file, delimiter=delimiter))
    merged_df = pd.concat(dfs, ignore_index=True)

    # Perform VLOOKUP operation with sellers.xlsx
    sellers_df = pd.read_excel("sellers.xlsx")
    merged_df = pd.merge(merged_df, sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')
    merged_df.rename(columns={'Seller_ID': 'SellerID'}, inplace=True)

    return merged_df

def main():
    st.title("CSV File Merger")

    # Allow user to upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files to merge", accept_multiple_files=True)

    if uploaded_files:
        output_file = "merged_file.csv"

        # Merge the uploaded CSV files
        merged_df = merge_csv_files(output_file, uploaded_files)

        # Select only specific columns
        selected_columns = ["SellerName", "Name", "Brand", "PrimaryCategory", "SellerID", "SellerSku"]
        merged_df = merged_df[selected_columns]

        # Save the selected columns to a CSV file
        merged_df.to_csv(output_file, index=False)

        # Offer download link for the merged CSV file
        st.markdown(f"### [Download merged CSV file]({output_file})")

        # Download button for the merged CSV file
        st.download_button(label="Download merged CSV file", data=open(output_file, "rb").read(), file_name=os.path.basename(output_file), mime="text/csv")

if __name__ == "__main__":
    main()
