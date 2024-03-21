import streamlit as st
import pandas as pd
import os
from datetime import datetime
import glob

# Function to merge CSV files, perform VLOOKUP, and update PrimaryCategory
def merge_csv_files(output_file, sellers_df, category_tree_df, csv_files):
    # Initialize an empty DataFrame with the additional columns
    result_df = pd.DataFrame(columns=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

    # Iterate through each CSV file
    for file in csv_files:
        try:
            # Check if the file is not empty and has a valid CSV file extension
            if pd.read_csv(file, nrows=1).empty:
                print(f"Skipping empty CSV file: {file}")
                continue

            # Print the column names of the current CSV file
            print(f"Columns in file {file}: {pd.read_csv(file, nrows=0).columns}")

            # Read the CSV file into a DataFrame, specifying the delimiter and extracting necessary columns
            df = pd.read_csv(file, delimiter=';', usecols=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

            # Check if the DataFrame has any data before processing
            if not df.empty:
                # Concatenate the selected columns to the result DataFrame
                result_df = pd.concat([result_df, df])

            else:
                print(f"Empty DataFrame in file: {file}. Skipping...")

        except pd.errors.EmptyDataError:
            print(f"No data to parse in file: {file}. Skipping...")
            continue
        except pd.errors.ParserError as e:
            print(f"Error reading file: {file}. Skipping...")
            print(f"Error details: {e}")
            continue

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Check if 'Category' column exists in category_tree_df
    if 'Category' in category_tree_df.columns:
        # Perform a VLOOKUP to replace "PrimaryCategory" values with corresponding values from "Category" column
        result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')

        # Fill NaN values in 'PrimaryCategory' with values from 'Category'
        result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])

        # Drop redundant columns
        result_df = result_df.drop(columns=['Category'])

    # Rearrange the columns
    result_df = result_df[["SellerName", "Name", "Seller_ID", "SellerSku", "PrimaryCategory", "Brand"]]

    # Generate the current date to include in the output file name
    current_date = datetime.now().strftime("%Y%m%d")

    # Write the merged DataFrame to the new CSV file
    result_df.to_csv(output_file, index=False)

    return output_file

# Streamlit app
def main():
    st.title("CSV File Merger")

    # Upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        st.write("Uploaded files:")
        for file in uploaded_files:
            st.write(file.name)

        # Upload Sellers Excel file
        sellers_file = st.file_uploader("Upload Sellers Excel file", type=["xlsx"])

        # Upload Category Tree Excel file
        category_tree_file = st.file_uploader("Upload Category Tree Excel file", type=["xlsx"])

        if sellers_file is not None and category_tree_file is not None:
            sellers_df = pd.read_excel(sellers_file)
            category_tree_df = pd.read_excel(category_tree_file)
            output_file = "Merged_skus_date.csv"

            # Call the function to merge the CSV files, perform VLOOKUP, and update PrimaryCategory
            result_file = merge_csv_files(output_file, sellers_df, category_tree_df, uploaded_files)

            st.success("Files successfully merged!")
            st.write("Download the merged CSV file:")
            st.download_button(label="Download Merged CSV", data=result_file, file_name=result_file, mime="text/csv")

if __name__ == "__main__":
    main()
