import streamlit as st
import pandas as pd
import os

def merge_csv_files(output_file, uploaded_files, delimiter=','):
    try:
        merged_df = pd.concat([pd.read_csv(file, delimiter=delimiter) for file in uploaded_files], ignore_index=True)
        return merged_df
    except pd.errors.ParserError:
        st.warning("One or more uploaded files are invalid CSV files and will be ignored.")

def main():
    st.title("CSV File Merger")

    # Allow user to upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files to merge", accept_multiple_files=True)

    if uploaded_files:
        output_file = "merged_file.csv"

        # Delimiter selection
        delimiter = st.selectbox("Select delimiter:", [',', ';'])

        # Merge the uploaded CSV files
        merged_df = merge_csv_files(output_file, uploaded_files, delimiter)

        if merged_df is not None:
            # Select only specific columns
            selected_columns = ["SellerName", "Name", "Brand", "PrimaryCategory"]
            merged_df = merged_df[selected_columns]

            # Save the selected columns to a CSV file
            merged_df.to_csv(output_file, index=False)

            # Offer download link for the merged CSV file
            st.markdown(f"### [Download merged CSV file]({output_file})")

            # Download button for the merged CSV file
            st.download_button(label="Download merged CSV file", data=open(output_file, "rb").read(), file_name=os.path.basename(output_file), mime="text/csv")

if __name__ == "__main__":
    main()
