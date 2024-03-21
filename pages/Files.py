import streamlit as st
import pandas as pd
import os
from datetime import datetime

def merge_csv_files(output_file, sellers_df, category_tree_df, uploaded_files):
    # Initialize an empty DataFrame with the additional columns
    result_df = pd.DataFrame(columns=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

    # Iterate through each uploaded CSV file
    for file in uploaded_files:
        try:
            # Read the CSV file into a DataFrame, specifying the delimiter and extracting necessary columns
            df = pd.read_csv(file, delimiter=';', usecols=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

            # Concatenate the selected columns to the result DataFrame
            result_df = pd.concat([result_df, df])

        except pd.errors.EmptyDataError:
            print(f"No data to parse in file: {file}. Skipping...")
            continue
        except pd.errors.ParserError as e:
            print(f"Error reading file: {file}. Skipping...")
            print(f"Error details: {e}")
            continue

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Perform a VLOOKUP to update PrimaryCategory
    if 'Category' in category_tree_df.columns:
        result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')
        result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])
        result_df = result_df.drop(columns=['Category'])
    else:
        print("'Category' column not found in category_tree_df. Skipping update.")

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
    return output_file

def main():
    # Title and file upload
    st.title("CSV File Merger")
    st.write("Upload CSV files to merge")

    uploaded_files = st.file_uploader("Choose CSV files to upload", type="csv", accept_multiple_files=True)

    if uploaded_files:
        # Display the uploaded file names
        st.write("Uploaded files:")
        for file in uploaded_files:
            st.write(file.name)

        # Specify the output file name
        output_file = "Merged_skus_date.csv"

        # Load the "sellers" Excel file
        sellers_df = pd.read_excel("sellers.xlsx")

        # Load the "category tree" Excel file
        category_tree_df = pd.read_excel("category_tree.xlsx")

        # Call the function to merge the CSV files, perform VLOOKUP, and update PrimaryCategory
        result_file = merge_csv_files(output_file, sellers_df, category_tree_df, uploaded_files)
        st.success(f"Result file saved as: {result_file}")

        # Add a download button for the result file
        st.download_button(
            label="Download merged file",
            data=result_file,
            file_name=result_file,
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
