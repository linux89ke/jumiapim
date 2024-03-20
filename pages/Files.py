import os
import pandas as pd
import streamlit as st
from datetime import datetime

def merge_csv_files(output_file, csv_files, sellers_df, category_tree_df):
    # Initialize an empty DataFrame with the additional columns
    result_df = pd.DataFrame(columns=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

    # Iterate through each CSV file
    for file in csv_files:
        try:
            # Check if the file is not empty and has a valid CSV file extension
            if pd.read_csv(file, nrows=1).empty:
                st.warning(f"Skipping empty CSV file: {file}")
                continue

            # Read the CSV file into a DataFrame, specifying the delimiter and extracting necessary columns
            df = pd.read_csv(file, delimiter=',', usecols=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

            # Check if the DataFrame has any data before processing
            if not df.empty:
                # Concatenate the selected columns to the result DataFrame
                result_df = pd.concat([result_df, df])

            else:
                st.warning(f"Empty DataFrame in file: {file}. Skipping...")

        except pd.errors.EmptyDataError:
            st.warning(f"No data to parse in file: {file}. Skipping...")
            continue
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {file}. Skipping...")
            st.error(f"Error details: {e}")
            continue

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Perform a VLOOKUP to update the "PrimaryCategory" column
    result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')
    result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])
    result_df = result_df.drop(columns=['Category'])

    # Generate the current date to include in the output file name
    current_date = datetime.now().strftime("%Y%m%d")

    # Write the merged DataFrame to the new CSV file
    result_df.to_csv(output_file, index=False)

    st.success(f"Merged data successfully written to {output_file}")

def main():
    st.title("CSV File Merger")

    # File uploader for CSV files
    st.sidebar.header("Upload Files")
    csv_files = st.sidebar.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    # File uploader for Excel files
    sellers_file = st.sidebar.file_uploader("Upload Sellers Excel file", type=["xlsx", "xls"])
    category_tree_file = st.sidebar.file_uploader("Upload Category Tree Excel file", type=["xlsx", "xls"])

    # Output file path
    output_file = "Merged_skus_date.csv"

    # Merge files when the user clicks the button
    if st.sidebar.button("Merge Files"):
        if not csv_files or not sellers_file or not category_tree_file:
            st.warning("Please upload all required files.")
        else:
            # Convert uploaded files to DataFrames
            csv_dfs = [pd.read_csv(csv_file) for csv_file in csv_files]
            sellers_df = pd.read_excel(sellers_file)
            category_tree_df = pd.read_excel(category_tree_file)

            # Merge CSV files
            merge_csv_files(output_file, csv_dfs, sellers_df, category_tree_df)

if __name__ == "__main__":
    main()
