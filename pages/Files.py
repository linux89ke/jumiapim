import os
import pandas as pd
import streamlit as st
import base64
from datetime import datetime

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
    result_df = pd.DataFrame()  # Initialize an empty DataFrame

    # Iterate through each CSV file
    for file in csv_files:
        try:
            df = pd.read_csv(file)  # Read the CSV file into a DataFrame
            result_df = pd.concat([result_df, df])  # Concatenate the DataFrame to the result DataFrame

        except pd.errors.EmptyDataError:
            print(f"No data to parse in file: {file}. Skipping...")
            continue

    # Load the "sellers" Excel file
    try:
        sellers_df = pd.read_excel(sellers_file)
    except pd.errors.EmptyDataError:
        print(f"No data to parse in file: {sellers_file}. Skipping...")
        sellers_df = pd.DataFrame(columns=["SellerName", "Seller_ID"])

    # Check if 'SellerName' column exists in sellers_df
    if 'SellerName' in sellers_df.columns:
        # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
        result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')
    else:
        print("'SellerName' column not found in sellers_df. Skipping merge.")

    # Write the merged DataFrame to the new CSV file
    result_df.to_csv(output_file, index=False)

    # Provide a link to download the output file
    st.markdown(get_binary_file_downloader_html(output_file), unsafe_allow_html=True)

def get_binary_file_downloader_html(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download CSV File</a>'
    return href

if __name__ == "__main__":
    st.title("CSV File Merger")

    # File uploader for CSV files
    st.sidebar.title("Upload CSV Files")
    uploaded_files = st.sidebar.file_uploader("Upload CSV files", accept_multiple_files=True, type="csv")

    if uploaded_files:
        # Specify the output file name
        current_date = datetime.now().strftime("%Y%m%d")
        output_file = f"Merged_skus_{current_date}.csv"

        # Call the function to merge the CSV files and perform VLOOKUP
        merge_csv_files(output_file, uploaded_files, "sellers.xlsx", "category_tree.xlsx")
