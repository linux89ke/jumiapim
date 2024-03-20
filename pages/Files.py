import os
import pandas as pd
import glob
from datetime import datetime

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
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
            df = pd.read_csv(file, delimiter=',', usecols=["SellerName", "SellerSku", "PrimaryCategory", "Name", "Brand"])

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

    # Load the "sellers" Excel file
    try:
        sellers_df = pd.read_excel(sellers_file)
    except pd.errors.EmptyDataError:
        print(f"No data to parse in file: {sellers_file}. Skipping...")
        sellers_df = pd.DataFrame(columns=["SellerName", "Seller_ID"])

    # Perform a VLOOKUP to add the "Seller_ID" column based on "SellerName"
    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    # Load the "category tree" Excel file
    try:
        category_tree_df = pd.read_excel(category_tree_file)
    except pd.errors.EmptyDataError:
        print(f"No data to parse in file: {category_tree_file}. Skipping...")
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
            print("'PrimaryCategory' column not found in result_df. Skipping update.")
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

if __name__ == "__main__":
    # Specify the output file name
    output_file = "Merged_skus_date.csv"

    # Specify the directory containing CSV files
    csv_files = glob.glob("Global*.csv")

    # Specify the sellers Excel file name
    sellers_file = "sellers.xlsx"

    # Specify the category tree Excel file name
    category_tree_file = "category_tree.xlsx"

    # Call the function to merge the CSV files, perform VLOOKUP, and update PrimaryCategory
    merge_csv_files(output_file, csv_files, sellers_file, category_tree_file)
