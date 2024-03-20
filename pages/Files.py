import streamlit as st
import pandas as pd
import os
from datetime import datetime

def merge_csv_files(output_file, csv_files, sellers_file, category_tree_file):
    if sellers_file is None:
        st.write("Please upload the sellers Excel file.")
        return
    if len(csv_files) == 0:
        st.write("Please upload at least one CSV file.")
        return

    result_df = pd.DataFrame(columns=[
        "SellerName", "Jumia SKU", "Name", "Brand", "Model", "Color", "PrimaryCategory", 
        "Categories", "BrowseNodes", "TaxClass", "ColorFamily", "MainMaterial", "ProductMeasures",
        "ProductWeight", "Description", "ShortDescription", "PackageContent", "CareLabel", 
        "YoutubeId", "AirCoolerType", "WashingMachineType", "VentingType", "Variation", 
        "StoveType", "JuicerType", "InstallationType", "FridgeType", "FreezerType", "FanType", 
        "DefrostType", "CookerType", "BlenderType", "ShopType", "ProductionCountry", 
        "ShelfLifeManaged", "MinimumShelfLife", "SaleStartDate", "SalePrice", "SaleEndDate", 
        "ProductWarranty", "ProductId", "Price", "SellerSku", "ParentSku", "Quantity", 
        "CreatedAt", "UpdatedAt", "ProductGroup", "Status"
    ])

    for file in csv_files:
        try:
            if pd.read_csv(file, nrows=1).empty:
                st.write(f"Skipping empty CSV file: {file.name}")
                continue

            df = pd.read_csv(file)

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

    try:
        sellers_df = pd.read_excel(sellers_file)
    except pd.errors.EmptyDataError:
        st.write(f"No data to parse in file: {sellers_file.name}. Skipping...")
        sellers_df = pd.DataFrame(columns=["SellerName", "Seller_ID"])

    result_df = result_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')

    try:
        category_tree_df = pd.read_excel(category_tree_file)
    except pd.errors.EmptyDataError:
        st.write(f"No data to parse in file: {category_tree_file}. Skipping...")
        category_tree_df = pd.DataFrame(columns=["PrimaryCategory", "Category"])

    if 'Category' in category_tree_df.columns:
        if 'PrimaryCategory' in result_df.columns:
            result_df = pd.merge(result_df, category_tree_df[['PrimaryCategory', 'Category']], left_on='PrimaryCategory', right_on='PrimaryCategory', how='left')
            result_df['PrimaryCategory'] = result_df['Category'].combine_first(result_df['PrimaryCategory'])
            result_df = result_df.drop(columns=['Category'])
        else:
            st.write("'PrimaryCategory' column not found in result_df. Skipping update.")
    else:
        st.write("'Category' column not found in category_tree_df. Skipping update.")

    result_df = result_df[[
        "SellerName", "Jumia SKU", "Name", "Brand", "Model", "Color", "PrimaryCategory", 
        "Categories", "BrowseNodes", "TaxClass", "ColorFamily", "MainMaterial", "ProductMeasures",
        "ProductWeight", "Description", "ShortDescription", "PackageContent", "CareLabel", 
        "YoutubeId", "AirCoolerType", "WashingMachineType", "VentingType", "Variation", 
        "StoveType", "JuicerType", "InstallationType", "FridgeType", "FreezerType", "FanType", 
        "DefrostType", "CookerType", "BlenderType", "ShopType", "ProductionCountry", 
        "ShelfLifeManaged", "MinimumShelfLife", "SaleStartDate", "SalePrice", "SaleEndDate", 
        "ProductWarranty", "ProductId", "Price", "SellerSku", "ParentSku", "Quantity", 
        "CreatedAt", "UpdatedAt", "ProductGroup", "Status"
    ]]

    current_date = datetime.now().strftime("%Y%m%d")

    if os.path.isfile(output_file):
        letter = 'A'
        while os.path.isfile(f"Merged_skus_{current_date}_{letter}.csv"):
            letter = chr(ord(letter) + 1)

        output_file = f"Merged_skus_{current_date}_{letter}.csv"

    result_df.to_csv(output_file, index=False)
    st.write("Merged file saved successfully.")

# Streamlit UI
st.title("CSV File Merger")

output_file = st.text_input("Enter output file name:", "Merged_skus_date.csv")
sellers_file = st.file_uploader("Upload sellers Excel file:")
category_tree_file = "category_tree.xlsx"

csv_files = st.file_uploader("Upload CSV files:", accept_multiple_files=True)
if st.button("Merge CSV Files"):
    merge_csv_files(output_file, csv_files, sellers_file, category_tree_file)
