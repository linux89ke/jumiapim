import os
import pandas as pd
from datetime import datetime
import streamlit as st

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
    # Initialize an empty DataFrame with the additional columns
    result_df = pd.DataFrame(columns=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

    # Iterate through each uploaded CSV file
    for file in csv_files:
        try:
            # Read the CSV file into a DataFrame, specifying the delimiter and extracting necessary columns
            df = pd.read_csv(file, delimiter=None, usecols=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

            # Check if the DataFrame has any data before processing
            if not df.empty:
                # Concatenate the selected columns to the result DataFrame
                result_df = pd.concat([result_df, df])

            else:
                st.warning(f"Empty DataFrame in file: {file.name}. Skipping...")

        except pd.errors.EmptyDataError:
            st.warning(f"No data to parse in file: {file.name}. Skipping...")
            continue
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {file.name}. Skipping...")
            st.error(f"Error details: {e}")
            continue

    # Load the "sellers" Excel file
    try:
        sellers_df = pd.read_excel(sellers_file)
    except pd.errors.EmptyDataError:
        st.warning(f"No data to parse in file: {sellers_file}. Skipping...")
        sellers_df = pd.DataFrame(columns=["SellerName", "Seller_ID"])

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Load the "category tree" Excel file
    try:
        category_tree_df = pd.read_excel(category_tree_file)
    except pd.errors.EmptyDataError:
        st.warning(f"No data to parse in file: {category_tree_file}. Skipping...")
        category_tree_df = pd.DataFrame(columns=["PrimaryCategory", "Category"])

    # Check if 'Category' column exists in category_tree_df
    if 'Category' in category_tree_df.columns:
        # Check if 'PrimaryCategory' column exists in result_df before updating
        if 'PrimaryCategory' in result_df.columns:
            # Perform a VLOOKUP to replace "PrimaryCategory" values with corresponding values from "Category" column
            result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')

            # Fill NaN values in 'PrimaryCategory' with values from 'Category'
            result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])

            # Drop redundant columns
            result_df = result_df.drop(columns=['Category'])
        else:
            st.warning("'PrimaryCategory' column not found in result_df. Skipping update.")
    else:
        st.warning("'Category' column not found in category_tree_df. Skipping update.")

    # Rearrange the columns
    result_df = result_df[["SellerName", "Name", "Seller_ID", "SellerSku", "PrimaryCategory", "Brand"]]

    # Generate the current date to include in the output file name
    current_date = datetime.now().strftime("%Y%m%d")

    # Check if the output file already exists
    if os.path.isfile(output_file):
        # Find a unique filename by appending a letter
        letter = 'A'
        while os.path.isfile(f"Merged_skus_{current_date}_{letter}.csv"):
            letter = chr(ord(letter) + 1)

        output_file = f"Merged_skus_{current_date}_{letter}.csv"

    # Write the merged DataFrame to the new CSV file
    result_df.to_csv(output_file, index=False)
    st.success(f"Merge completed. Merged data saved to {output_file}")

    # Provide a download link for the merged result
    st.markdown(f"### [Download Merged Data]({output_file})")

if __name__ == "__main__":
    # Specify the output file name
    output_file = "Merged_skus_date.csv"

    # File uploader for CSV files
    st.title("Merge CSV Files")
    csv_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

    if csv_files:
        merge_csv_files(output_file, csv_files, "sellers.xlsx", "category_tree.xlsx")
