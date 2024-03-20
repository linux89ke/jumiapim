import streamlit as st
import pandas as pd
import os
from datetime import datetime

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
    # Check if sellers Excel file and at least one CSV file are uploaded
    if sellers_file is None:
        st.write("Please upload the sellers Excel file.")
        return
    if len(csv_files) == 0:
        st.write("Please upload at least one CSV file.")
        return

    # Initialize an empty DataFrame with the additional columns
    result_df = pd.DataFrame(columns=["SellerName", "Jumia SKU", "Name", "Brand", "PrimaryCategory"])

    # Iterate through each CSV file
    for file in csv_files:
        try:
            # Check if the file is not empty and has a valid CSV file extension
            if pd.read_csv(file, nrows=1).empty:
                st.write(f"Skipping empty CSV file: {file.name}")
                continue

            # Read the CSV file into a DataFrame, specifying the delimiter and extracting necessary columns
            df = pd.read_csv(file, usecols=["SellerName", "Jumia SKU", "Name", "Brand", "PrimaryCategory"])

            # Check if the DataFrame has any data before processing
            if not df.empty:
                # Concatenate the selected columns to the result DataFrame
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
        except ValueError as e:
            st.write(f"Error reading file: {file.name}. Skipping...")
            st.write(f"Error details: {e}")
            continue

    # Load the "sellers" Excel file
    try:
        sellers_df = pd.read_excel(sellers_file)
    except pd.errors.EmptyDataError:
        st.write(f"No data to parse in file: {sellers_file.name}. Skipping...")
        sellers_df = pd.DataFrame(columns=["SellerName", "Seller_ID"])

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Load the "category tree" Excel file
    try:
        category_tree_df = pd.read_excel(category_tree_file)
    except pd.errors.EmptyDataError:
        st.write(f"No data to parse in file: {category_tree_file}. Skipping...")
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
            st.write("'PrimaryCategory' column not found in result_df. Skipping update.")
    else:
        st.write("'Category' column not found in category_tree_df. Skipping update.")

    # Rearrange the columns
    result_df = result_df[["SellerName", "Jumia SKU", "Name", "Brand", "PrimaryCategory"]]

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
    st.write("Merged file saved successfully.")

# Streamlit UI
st.title("CSV

         
