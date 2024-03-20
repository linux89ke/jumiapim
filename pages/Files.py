import streamlit as st
import pandas as pd
import os
from datetime import datetime
import glob

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
    if not csv_files:
        st.write("No CSV files uploaded. Please upload CSV files.")
        return

    result_df = pd.DataFrame(columns=["SellerName", "Name", "Seller_ID", "SellerSku", "PrimaryCategory", "Brand"])

    for file in csv_files:
        try:
            if pd.read_csv(file, nrows=1).empty:
                st.write(f"Skipping empty CSV file: {file.name}")
                continue

            df = pd.read_csv(file, delimiter='\t', usecols=["SellerName", "Name", "SellerSku", "PrimaryCategory", "Brand"])

            if not df.empty:
                result_df = pd.concat([result_df, df])
            else:
                st.write(f"Empty DataFrame in file: {file.name}. Skipping...")

        except pd.errors.EmptyDataError:
            st.write(f"No data to parse in file: {file.name}. Skipping...")
            continue
        except pd.errors.ParserError as e:
            st.write(f"Error reading file: {file.name}. Skipping...")
            st.write(f"Error details: {e}")
            continue

    if sellers_file is not None:
        try:
            sellers_df = pd.read_excel(sellers_file)
            result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')
        except pd.errors.EmptyDataError:
            st.write(f"No data to parse in file: {sellers_file.name}. Skipping...")
        except KeyError:
            st.write("Unable to merge sellers data. Ensure 'SellerName' and 'Seller_ID' columns exist in sellers file.")

    if category_tree_file is not None:
        try:
            category_tree_df = pd.read_excel(category_tree_file)
            if 'Category' in category_tree_df.columns and 'PrimaryCategory' in result_df.columns:
                result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')
                result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])
                result_df = result_df.drop(columns=['Category'])
        except pd.errors.EmptyDataError:
            st.write(f"No data to parse in file: {category_tree_file}. Skipping...")

    current_date = datetime.now().strftime("%Y%m%d")
    if os.path.isfile(output_file):
        letter = 'A'
        while os.path.isfile(f"Merged_skus_{current_date}_{letter}.csv"):
            letter = chr(ord(letter) + 1)
        output_file = f"Merged_skus_{current_date}_{letter}.csv"

    result_df = result_df[["SellerName", "Name", "Seller_ID", "SellerSku", "PrimaryCategory", "Brand"]]

    result_df.to_csv(output_file, index=False)
    st.write("Merged file saved successfully.")

# Streamlit UI
st.title("CSV File Merger")

output_file = st.text_input("Enter output file name:", "Merged_skus_date.csv")
sellers_file = st.file_uploader("Upload sellers Excel file (optional):", type=['xlsx'])
category_tree_file = st.file_uploader("Upload category tree Excel file (optional):", type=['xlsx'])

csv_files = st.file_uploader("Upload CSV files:", accept_multiple_files=True)

if st.button("Merge CSV Files"):
    merge_csv_files(output_file, csv_files, sellers_file, category_tree_file)
